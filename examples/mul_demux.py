from pyDXHR.MUL import MUL

# never_asked_for_this = r"pc-w\audio\streams\vo\eng\det1\adam_jensen\sq02\det1_sq02_dia_adam_006b.mul"
never_asked_for_this = r"F:\DXHR_bigfiles\DXHRDC_Unpacked\FFFFE081\pc-w\audio\streams\vo\eng\det1\adam_jensen\sq02\det1_sq02_dia_adam_006b.mul"
claymore = r"F:\DXHR_bigfiles\DXHRDC_Unpacked\default\pc-w\audio\streams\character\adam\augmentations\aug_claymore\aug_claymore_08.mul"

mul = MUL.from_file(claymore)
mul.open()

fsb = mul.to_fsb(r"C:\Users\vardo\Documents\pyDXHR\playground\mul\test_1.fsb")

breakpoint()
