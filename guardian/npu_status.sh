#!/bin/bash
# Quick NPU status check

echo ""
echo "NPU STATUS - $(date '+%H:%M:%S')"

# Driver status
if lsmod | grep -q galcore; then
    echo "✅ Driver: LOADED"
else
    echo "❌ Driver: NOT LOADED"
fi

# Device status
if [ -e /dev/galcore ]; then
    echo "✅ Device: PRESENT"
else
    echo "❌ Device: MISSING"
fi

# NPU version
echo "NPU Version:"
dmesg | grep -i npu_version | tail -1

echo ""

