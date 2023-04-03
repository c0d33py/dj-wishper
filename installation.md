# Install NVIDIA GPU Drivers

## 1. Update && upgrade the package database

    sudo apt update -y && sudo apt upgrade -y

## 2. To detect the NVIDIA card, we need to install nvidia-detect

    sudo apt install nvidia-detect

## 3. Run nvidia-detect

    sudo nvidia-detect

## 4. Install the driver

    sudo apt install -y nvidia-driver nvidia-cuda-toolkit

## 5. Reboot

    sudo reboot -f

## 6. Check the driver

    nvidia-smi 

## 7. If mesa-opencl-icd is installed, we should remove it

    sudo apt remove mesa-opencl-icd

## 8. install cudnn sudo

***To install cudnn, we need to download the deb file from NVIDIA website. avoide the libnvidia-cfg1_450.51.06-0ubuntu0.18.04.1_amd64.deb file, it will cause the system crash***

    apt install nvidia-cudnn

margin: 0 0 4px 0;
    line-height: 40px;
    overflow: hidden;
    display: block;
    max-height: 9rem;
    -webkit-line-clamp: 3;
    display: box;
    display: -webkit-box;
    -webkit-box-orient: vertical;
    text-overflow: ellipsis;
    white-space: normal;
