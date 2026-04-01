R102825
    improved locking mechanism for better handling multiple threads sccb access
    fixed preview issue in some eg0198 ovd file
R090825 ¶
    fixed bug in 8 bit raw image callback
    clean up python example code
R080125
    improve sccb stability
    prepare for i3c dongle support
R051925
    improved burst read performance in Venus eval kit
    EG0198 dlls to VS2019 using C++17 standard
    internal release will not check FPGA version anymore
R042325
    updated api based on latest vpl mcu:64 200a0ff4 = 80210425
    improve vc channel change preview success rate
R041725
    remove 32 bit i2c access limit to device id 0x64 in venus system
R041525
    formalized 32bit address and 32 bit data support in venus system
    added i3c (with venus pro lite)support
    added VPL specific controls such as vc mapping/ mipi lane mapping / merge mode
    added callback example in python
    bug fixes
Note, the minimum VPL version requirement for i3c support and advanced functions
64 200a0ff0 = 0x80260225
64 200a0ff4 = 0x80030325