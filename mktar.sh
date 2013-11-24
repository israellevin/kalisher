#!/bin/bash

chrootdir=chroot
overlaydir=overlay
targetdir=$(dirname "$(readlink -f "$0")")
mirror=http://ftp.debian.org/debian
mirror=http://debian.co.il/debian
packages=linux-image-686-pae
packages="$packages bash-completion bc bsdmainutils git grub-pc mc moreutils tmux unzip unrar vim"
packages="$packages ca-certificates curl dhcpcd iproute netbase openssh-server sshfs w3m wget"
packages="$packages alsa-base alsa-utils firmware-ipw2x00 imagemagick mplayer2"

if ! pushd "$chrootdir"; then
    echo creating tmpfs
    mkdir "$chrootdir"
    mount -t tmpfs -o size=60% none "$chrootdir" || exit 1
    pushd "$chrootdir"
fi

if [ ! -f sbin/init ]; then
    echo debootstrapping
    debootstrap --variant=minbase sid . "$mirror"
fi

echo deb $mirror sid main contrib non-free > etc/apt/sources.list
echo deb http://debian.tu-bs.de/project/aptosid/debian/ sid main fix.main >> etc/apt/sources.list
chroot . apt-get update
chroot . apt-get --no-install-recommends --force-yes -y install $packages
chroot . dpkg-reconfigure tzdata
chroot . adduser i
chroot . addgroup wheel
chroot . adduser i wheel
chroot . adduser i audio
chroot . adduser i video
chroot . adduser i disk
chroot . adduser i fuse
chroot . passwd -d root

rsync -av "../$overlaydir/" .
rm -rf --one-file-system dev proc tmp mnt
mkdir dev proc
mkdir -m 777 tmp mnt
gettarget(){
    if [ -d "$tr" ]; then
        read -n 1 -p "copy to $tr? (Y/n) " q; echo; echo
        [ n = "$q" ] || return 0
        tr=''
    else
        read -p "destination ($targetdir): " tr && [ "$tr" ] || tr="$targetdir"
    fi
    gettarget
}
gettarget
tar cf - . | pv -s $(du -sb . | awk '{print $1}') > "$tr/ars.tar"
