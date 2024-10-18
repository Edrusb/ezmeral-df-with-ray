#!/bin/bash

########################################################################
# ray-install.sh - a simple script to install Ray on Linux
# Copyright (C) 2024 Denis Corbin
#
#  ray-install.sh is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  ray-install.sh is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Webdar.  If not, see <http://www.gnu.org/licenses/>
#
########################################################################


###
#
# airgap environment support
#
###
#
# this script replies on the distro package management tools and on python3-pip:
# - For the first, the distro repositories are assumed to be setup accordingly
#   to the provided repository in the airgap environment, so nothing specific
#   need to be done.
# - For the second (pip) a repository must be set in the airgap environment and
#   and its URL provided as second argument to this script as described in the
#   "usage" function below
#

usage()
{
    local argv0="$1"

    echo ""
    echo "usage: $argv0 <installation path> [ <airgap pip repo URL> ]"
    echo ""
    exit 1
}

fecho()
{
    # behaves like echo but returning a failure exit code

    echo $*
    return 1
}

add_lsb_release()
{
    if ! lsb_release --id 1> /dev/null 2> /dev/null ; then
	yum install redhat-lsb-core -y 1> /dev/null 2> /dev/null
	apt-get install lsb-release -y 1> /dev/null 2> /dev/null
    fi

    if ! lsb_release --id 1> /dev/null 2> /dev/null ; then
	return 1
    else
	return 0
    fi
}


get_distro_type()
{

    if lsb_release --id 1> /dev/null 2> /dev/null ; then
	echo $(lsb_release --id | sed -rn -e 's/^Distributor ID:\s+//p')
    else
	echo "Can't determine distro name"
	exit 1
    fi
}

install_rocky()
{
    local install_path="$1"

    yum install -y gcc-c++ cmake git              || fecho "failed installing prerequired packages" || exit 2
    python3 -m venv "$install_path"               || fecho "failed creating virtual env at $install_path" || exit 2
    source "$install_path"/bin/activate           || fecho "failed activating virtual env at $install_path" || exit 2
    python3 -m pip install $PIPREP -U pip         || fecho "failed upgrading pip" || exit 2
    python3 -m pip install $PIPREP --upgrade pip  || fecho "failed upgrading pip" || exit 2
    python3 -m pip install $PIPREP setuptools-scm || fecho "failed installing setuptools-scm" || exit 2
    python3 -m pip install $PIPREP -U ray[all]    || fecho "failed installing Ray[all]" || exit 2
}

install_debian()
{
    local install_path="$1"

    apt-get install -y g++ cmake git              || fecho "failed installing prerequired packages" || exit 2
    apt-get install -y python3-pip                || fecho "failed installing python3-pip" || exit 2
    apt-get install -y python3-venv               || fecho "failed installing python3-venv" || exit 2
    python3 -m venv "$install_path"               || fecho "failed creating virtual env at $install_path" || exit 2
    source "$install_path"/bin/activate           || fecho "failed activating virtual env at $install_path" || exit 2
    python3 -m pip install $PIPREP -U ray[all]    || fecho "failed installing Ray[all]" || exit 2
}

if [ -z "$1" ] ; then
    usage "$0"
    exit 1
else
    install_path="$1"
fi

if [ -z "$2" ] ; then
    PIPREP=""
else
    PIPREP="--index-url $2"
fi

if ! add_lsb_release ; then
    echo "lsb_release command needed but could not be found nor installed"
    echo "Please provide it/install it to let this script determine"
    echo "the distro type it is run under"
    exit 1
fi

distro=$(get_distro_type)

case "$distro" in
    Debian|debian|ubuntu|Ubuntu)
	install_debian "$install_path"
	;;
    Rocky|rocky|Redhat|redhat)
	install_rocky "$install_path"
	;;
    *)
	echo "Unsupported distro: $distro"
	echo "Aborting"
	exit 1
esac

echo ""
echo " Ray installation completed!"
echo ""
echo " You can now launch go_ray with the same install_path as given here"
echo ""
