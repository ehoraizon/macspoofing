"""This script  works only on windows.
if you wan to change your mac address on linux use macchanger"""

import winreg
import argparse
import sys

def parse_arg():
    parser = argparse.ArgumentParser(description="If you already change your MAC you don't have to introduce any data")
    parser.add_argument("-mac", "--newMAC", help="Chose your new MAC address. Example: -mac 10-20-30-40-50-60")
    parser.add_argument("-old", "--oldMAC", help="Write your default MAC of the iface. Example: -old 11-22-33-44-55-66")
    parser.add_argument("-i", "--iface", help="Chose the iface name. Example: -i wlan0")
    return parser.parse_args()

class Error(Exception):
    def msg(self, ms):
        print("\n"+ms)
        input("PRESS ENTER TO CONTINUE")
        sys.exit()
         
class MacChange:
    def __init__(self):
        args = parse_arg()
        self.MAC = args.newMAC
        self.OLD_MAC = args.oldMAC
        if self.MAC != None:
            self.MAC = self.MAC.replace("-", '').replace(":", '')
            if self.OLD_MAC == None:
                raise Error().msg("YOU HAVE TO INTROUDCE YOUR OLD MAC")
            self.OLD_MAC = self.OLD_MAC.replace("-", '').replace(":", '')
        self.IFACE = args.iface
        self.FOLDER = ''
        self.local = winreg.HKEY_LOCAL_MACHINE
        self.acces = winreg.KEY_ALL_ACCESS
        self.valor = winreg.REG_SZ
        self.source_look = r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}'
        self.master_key = winreg.OpenKey(self.local,  self.source_look)
        
    def get_folder(self):
        '''Search and stole the folder where the iface'''
        max_folder = winreg.QueryInfoKey(self.master_key)[0] - 1
        
        for folder in range(0, max_folder):
            if folder < 10:
                try:
                    with winreg.OpenKey(self.local, self.source_look + '\\000' + str(folder)) as key:
                        if winreg.QueryValueEx(key, 'DriverDesc')[0] == self.IFACE:
                            self.FOLDER = '\\000' + str(folder)
                except:
                    pass
            else:
                try:
                    with winreg.OpenKey(self.local, self.source_look + '\\00' + str(folder)) as key:
                        if winreg.QueryValueEx(key, 'DriverDesc')[0] == self.IFACE:
                            self.FOLDER = '\\00' + str(folder) 
                except:
                    pass
                    
        if self.FOLDER == '':
            raise Error().msg("NO DRIVER FOUND WITH THE NAME IFACE")
            
    def change(self):
        '''Change the MAC address of the chosen iface'''
        path = r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}' + self.FOLDER
        try:
            with winreg.OpenKey(self.local, path, 0, self.acces) as key:
                winreg.SetValueEx(key, "NetworkAddress", 0,  self.valor, self.MAC)
        except:
            raise Error().msg(str(sys.exc_info()[1]))
            
    def default(self):
        '''Change the MAC address to default'''
        with open('MAC.temp', 'rt') as file:
            folder = file.readline().replace('\n','').replace(' ', '')
            path = r'SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}' + folder
            with winreg.OpenKey(self.local, path, 0, self.acces) as key:
                winreg.SetValueEx(key, "NetworkAddress", 0,  self.valor, file.readline())
    
    def save_MAC(self):
        '''Save the MAC address and the FOLDER in the file MAC.temp'''
        with open("MAC.temp", "wt") as file:
            file.write(self.FOLDER + ' \n')
            file.write(self.OLD_MAC)
            
    def start(self):
        if self.MAC == None and self.OLD_MAC == None and self.IFACE == None:
            try:
                self.default()
            except FileNotFoundError:
                raise Error().msg("FILE MAC.temp NOT FOUND, CHANGE YOUR MAC ADDRESS")
            return 1
        else:
            self.get_folder()
            self.save_MAC()
            self.change()
            return 0
        
class NameChange:
    def __init__(self):
        self.user = winreg.HKEY_LOCAL_MACHINE
        self.path = r'SYSTEM\CurrentControlSet\services\Tcpip\Parameters'
        self.valor = winreg.REG_SZ
        self.NAME_PC = ''
    
    def change(self):
        '''Change the name of the PC in the network'''
        with winreg.OpenKeyEx(self.user, self.path) as key:
            self.NAME_PC = winreg.QueryValueEx(key, "Hostname")[0]
        if self.NAME_PC == '':
            raise Error().msg("YOU DONT HAVE A NAME")
        with winreg.CreateKeyEx(self.user, self.path) as key:
            winreg.SetValueEx(key, "Hostname", 0,  self.valor, '')
            winreg.SetValueEx(key, "NV Hostname", 0,  self.valor, '')
            
    def default(self):
        '''Change to default the name of the PC in the network'''
        with open('NAME.temp', 'rt') as file:
            self.NAME_PC = file.readline()
        with winreg.CreateKeyEx(self.user, self.path) as key:
            winreg.SetValueEx(key, "Hostname", 0,  self.valor, self.NAME_PC)
            winreg.SetValueEx(key, "NV Hostname", 0,  self.valor, self.NAME_PC)
            
    def save_NAME(self):
        """Save the PC name"""
        with open('NAME.temp', 'wt') as file:
            file.write(self.NAME_PC)
            
    def start(self, arg):
        if arg == 1:
            try:
                self.default()
            except FileNotFoundError:
                raise Error().msg("FILE NAME.temp NOT FOUND, CHANGE YOUR MAC ADDRESS")
        
        else:   
            self.change()
            self.save_NAME()
            
if __name__ == "__main__":
    print("\nAFTER THE SCRIPT FINISH YOU NEED REESTART YOUR DRIVER")
    res = MacChange().start()
    NameChange().start(res)
    