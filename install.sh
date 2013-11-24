#!/bin/sh
[ -f ars.tar ] || ./mktar.sh
if [ "$1" ]; then
    target=$1
else
    target=.
fi
shift
tar xf ars.tar -C "$target"
if [ "$1" ]; then
    device=$1
else
    device=/dev/sda
fi
mount --bind /dev "$target/dev"
chroot $target grub-install $device
chroot $target update-grub2
umount "$target/dev" || exit 1
exit 0
