#!/bin/bash

########################################################################
# go-ray.sh - a simple script to install Ray on Linux
# Copyright (C) 2024 Denis Corbin
#
#  go-ray.sh is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  go-ray.sh is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Webdar.  If not, see <http://www.gnu.org/licenses/>
#
########################################################################


usage()
{
    local argv0="$1"

    echo ""
    echo "usage: $argv0 <installation path> { head | worker <head IP> } "
    echo "       $argv0 <installation path> stop"
    echo ""
    exit 1
}

run_worker()
{
    local install_path="$1"
    local ray_head_ip="$2"

    ulimit -n 102400
    source "$install_path"/bin/activate

    ray start --address="${ray_head_ip}:6379"
}

run_head()
{
    local install_path="$1"

    ulimit -n 102400
    source "$install_path"/bin/activate
    ray start --head --dashboard-host 0.0.0.0 --disable-usage-stats
}

ray_stop()
{
    local install_path="$1"

    source "$install_path"/bin/activate
    ray stop
}


if [ -z "$1" -o -z "$2" ] ; then
    usage "$0"
    exit &
fi

install_path="$1"
action_type="$2"
option="$3"

case "$action_type" in
    head)
	run_head "$install_path"
	;;
    worker)
	if [ -z "$3" ] ; then
	    usage "$0"
	else
	    run_worker "$install_path" "$3"
	fi
	;;
    stop)
	ray_stop "$install_path"
	;;
    *)
	usage "$0"
esac





