#!/bin/sh

# Stage defination:
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo Stage Info:
echo BIT0: IPC_1SNR_SC4336P_AOV
echo BIT7: IPC_1SNR_imx415_LINUX
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"


if [ -z "$1" ]; then
    # BOARD: IPC_1SNR_SC4336P_AOV
    source ./cases/iford_cases/aov/setup.sh
    source ./cases/iford_cases/interrupts/setup.sh
    source ./cases/iford_cases/cpu/setup.sh
    source ./cases/iford_cases/memory/setup.sh
    source ./cases/iford_cases/idac/setup.sh

    # BOARD: IPC_1SNR_imx415_LINUX
    source ./cases/iford_cases/ut/setup.sh
else
    # BOARD: IPC_1SNR_SC4336P_AOV
    source ./cases/iford_cases/aov/setup.sh $1

    # BOARD: IPC_1SNR_imx415_LINUX
    source ./cases/iford_cases/ut/setup.sh $1
fi
