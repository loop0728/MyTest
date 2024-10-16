#!/bin/sh

# Stage defination:
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo Stage Info:
echo BIT0: SYS_IPC_1SNR_SC4336P_AOV
echo BIT1: SYS_IPC_1SNR_IMX415_LINUX
echo BIT2: SYS_IPC_2SNR_SC4336P_LINUX
echo BIT3: SYS_IPC_1SNR_IMX415_DUALOS
echo BIT7: SYS_UT_IPC_1SNR_imx415_LINUX
echo BIT9: BSP
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"


if [ -z "$1" ]; then
    source ./cases/platform/sys/setup.sh
    source ./cases/platform/bsp/setup.sh
else
    source ./cases/platform/sys/setup.sh $1
    source ./cases/platform/bsp/setup.sh $1
fi
