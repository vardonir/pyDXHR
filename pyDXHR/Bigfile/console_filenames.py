def textures_ids(bigfile):
    data = bigfile.read("textures.ids")
    lines = [l.decode("latin1").split(",") for l in data.strip().split(b"\r\n")]
    return {int(l[0]): l[1] for i, l in enumerate(lines) if i != 0}


def dtpdata_ids(bigfile):
    data = bigfile.read("dtpdata.ids")
    lines = [l.decode("latin1").split(",") for l in data.strip().split(b"\r\n")]
    return {int(l[0]): l[1] for i, l in enumerate(lines) if i != 0}
