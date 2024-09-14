#!/bin/sh

# Stage defination:
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
echo Stage Info:
echo BIT0: IPC_1SNR_SC4336P_AOV
echo BIT7: IPC_1SNR_imx415_LINUX
echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"

# BOARD: IPC_1SNR_SC4336P_AOV
source ./Cases/Iford_cases/AOV/setup.sh
source ./Cases/Iford_cases/Interrupts/setup.sh
source ./Cases/Iford_cases/IDAC/setup.sh

# BOARD: IPC_1SNR_imx415_LINUX
source ./Cases/Iford_cases/UT/setup.sh
