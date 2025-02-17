# -*- coding: utf-8 -*-
#
# Copyright(C) 2021 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

from convert2rhel.systeminfo import system_info
from convert2rhel.utils import mkdir_p, run_subprocess


OPENJDK_RPM_STATE_DIR = "/var/lib/rpm-state/"

logger = logging.getLogger(__name__)


def check_and_resolve():
    remove_iwlax2xx_firmware()


def remove_iwlax2xx_firmware():
    """Resolve a yum transaction failure on OL8 related to the iwl7260-firmware and iwlax2xx-firmware.

    The iwl7260-firmware package causes a file conflict error while trying to replace it with its RHEL counterpart.
    The reason for this happening is that the iwlax2xx-firmware is an dependency package of iwl7260-firmware in OL8,
    but in the RHEL repositories, this dependency doesn't exist, all of the files that are available under the
    iwlax2xx-firmware package in OL8, are in fact, available in the iwl7260-firmware package in RHEL, thus, we are
    removing this depedency to not cause problems with the conversion anymore.

    Related: https://bugzilla.redhat.com/show_bug.cgi?id=2078916
    """
    iwl7260_firmware = system_info.is_rpm_installed(name="iwl7260-firmware")
    iwlax2xx_firmware = system_info.is_rpm_installed(name="iwlax2xx-firmware")

    logger.info("Checking if the iwl7260-firmware and iwlax2xx-firmware packages are installed.")
    if system_info.id == "oracle" and system_info.version.major == 8:
        # If we have both of the firmware installed on the system, we need to remove the later one,
        # iwlax2xx-firmware, since this causes problem in the OL8 conversion in the replace packages step.
        if iwl7260_firmware and iwlax2xx_firmware:
            logger.info(
                "Removing the iwlax2xx-firmware package. Its content is provided by the RHEL iwl7260-firmware"
                " package."
            )
            _, exit_code = run_subprocess(["rpm", "-e", "--nodeps", "iwlax2xx-firmware"])
            if exit_code != 0:
                logger.error("Unable to remove the package iwlax2xx-firmware.")
        else:
            logger.info("The iwl7260-firmware and iwlax2xx-firmware packages are not both installed. Nothing to do.")
    else:
        logger.info("Relevant to Oracle Linux 8 only. Skipping.")
