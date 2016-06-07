import sys, argparse
marker = 'qwerty'

class HideException(Exception):   
    pass

class ExtractException(Exception):
	pass

def bin(s):
    return str(s) if s <= 1 else bin(s >> 1) + str(s & 1)


def byte2bin(bytes):    
    for b in bytes:
        yield bin(ord(b)).zfill(8)


def decrypt_char(container):   
    sbits = ''
    for cbits in byte2bin(container):
        sbits += cbits[-1]
        if len(sbits) == 8:
            yield chr(int(sbits, 2))
            sbits = ''



def extract(bmp_filename):
    bmp = open(bmp_filename, 'rb')
    bmp.seek(55)
    container = bmp.read()
    bmp.close()

    decrypted = []
    for b in decrypt_char(container):
        decrypted.append(b)        
        if (len(marker) == len(decrypted) and
            marker != ''.join(decrypted)):
            raise ExtractException('The image %s does not contain confidential file.', bmp_filename)
    if len(decrypted) > len(marker):        
        decrypted = ''.join(decrypted).split(marker)
        src_filename = decrypted[1]
        src_data = decrypted[2]
        src = open(src_filename, 'wb')
        src.write(src_data)
        src.close()


def hide(bmp_filename, src_filename):    
    src = open(src_filename, 'rb')
    secret = marker + src_filename + marker + src.read() + marker
    src.close()

    bmp = open(bmp_filename, 'rb+')
    bmp.seek(55)
    container = bmp.read()

    need = 8 * len(secret) - len(container)
    if need > 0:
        raise HideException('BMP size is not sufficient for confidential file.'
                            '\nNeed another %s byte.' % need)
    cbits = byte2bin(container)
    encrypted = []
    for sbits in byte2bin(secret):
        for bit in sbits:
            bits = cbits.next()           
            bits = bits[:-1] + bit
            b = chr(int(bits, 2))            
            encrypted.append(b)

    bmp.seek(55)
    bmp.write(''.join(encrypted))
    bmp.close()

def main():
    bmp_filename = ''
    src_filename = ''    
    parser = argparse.ArgumentParser(description='new')
    parser.add_argument('-i','--input', type = str, help='BMP file name', required=True)
    parser.add_argument('-s','--output',type = str, help='Secret file name',default='')
    parser.add_argument('-e','--enc',help='encrypted',action = 'store_true', default = False)
    parser.add_argument('-d','--dec',help='decrypted',action = 'store_true', default = False)
    args = parser.parse_args()
    if args.enc==False and args.dec==False:
        print('Usage -e or -d')
        return 1
    if args.enc and args.output=='':
        print('No hide file\n'
              'Usage: new.py -i [input] -s [hide] -e/-d')
        return 1
    if args.enc:
        hide(args.input, args.output)
    if args.dec:
        extract(args.input)

if __name__ == '__main__':
    main()
