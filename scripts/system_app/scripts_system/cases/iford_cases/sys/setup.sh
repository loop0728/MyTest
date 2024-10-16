#!/bin/sh

if [ -z "$1" ]; then
    # BOARD: IPC_1SNR_SC4336P_AOV
    source ./cases/platform/sys/aov/setup.sh
    source ./cases/platform/sys/interrupts/setup.sh
    source ./cases/platform/sys/cpu/setup.sh
    source ./cases/platform/sys/memory/setup.sh
    source ./cases/platform/sys/idac/setup.sh

    # BOARD: IPC_1SNR_imx415_LINUX
    source ./cases/platform/sys/ut/setup.sh
else
    # BOARD: IPC_1SNR_SC4336P_AOV
    source ./cases/platform/sys/aov/setup.sh $1

    # BOARD: IPC_1SNR_imx415_LINUX
    source ./cases/platform/sys/ut/setup.sh $1
fi
