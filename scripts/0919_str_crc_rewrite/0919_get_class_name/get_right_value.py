key = "overdrive"
line = "overdrive=3"
#key = "bootargs"
#line = "bootargs=root=/dev/ram rdinit=/linuxrc initrd=0x21800000,0x60000 rootwait LX_MEM=0x4000000 cma=2M os_adaptor=mma_base=0x24000000,mma_size=0xb000000 loglevel=3 maxcpus=1 mtdparts=nor0:0x5F000(BOOT),0x1000(ENV),0x240000(KERNEL),0x220000(rootfs),0xA0000(MISC),0x230000(RO_FILES),0x170000(RTOS),0x60000(RAMDISK),0x530000(miservice),0x110000(customer) nohz=off"
#val = line.strip().split('=')[1]
index = line.find('=')
val = line[index+1:]
print(f"the whole line:{line}")
print(f"the value of key:{key} is {val}")
