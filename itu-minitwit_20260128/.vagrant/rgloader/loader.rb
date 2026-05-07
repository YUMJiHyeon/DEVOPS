# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: BUSL-1.1

# This file loads the proper rgloader/loader.rb file that comes packaged
# with Vagrant so that encoded files can properly run with Vagrant.
require File.expand_path(
    "rgloader/loader", ENV["VAGRANT_INSTALLER_EMBEDDED_DIR"]) 
if ENV["VAGRANT_INSTALLER_EMBEDDED_DIR"]
else
  raise RuntimeError, "Encoded files can't be read outside of the Vagrant installer."
end
