"""Container for makems wrapper and all parts of it"""

from __future__ import print_function

import os
import shutil
import subprocess
import tempfile


#Read makems config file into dictionary
def cfg_read(
            cfgfile,  # some default config file
            ):
    fin = open(cfgfile, 'r')
    config = fin.readlines()
    fin.close()
    cfg_dict = {}
    for line in config:
        [key, value] = line.strip().split('=')
        if key in cfg_dict:
            raise RuntimeError('Duplicate key %s' % key)
        cfg_dict[key] = value
    return cfg_dict


#Fake file for makems input
def cfg_write_ms(cfg_file, cfg_dict, verbose=False):
    for key, value in cfg_dict.iteritems():
        # cfg_file.write('%s\n'%('='.join((key, str(value)))))
        print('='.join((key, str(value))), file=cfg_file)
        if verbose:
            print('='.join((key, str(value))))


#Make empty measurement set
def ms_make(opts):
    cfg_dict = cfg_read(opts.cfg)
    ntimesteps = (opts.synthesis/opts.dt) / (12./opts.dtime)
    if opts.msname is None:
        msname = '%s_%s_%s.ms' % (opts.array, opts.declination, opts.stime.replace('/', '-'))
    else:
        msname = '%s_%s_%s.ms' % (opts.array, opts.declination, opts.stime.replace('/', '-'))
    if opts.tblname is None:
        opts.tblname = 'ANTENNAS'
    # generate makems config file
    cfg_dict.update({
       'NParts': opts.nparts,
       'NBands': opts.nbands,
       'NFrequencies': opts.nfreqs,
       'StartFreq': opts.sfreq,
       'StepFreq': opts.stepfreq,
       'StartTime': opts.stime,
       'StepTime': opts.dt,
       'NTimes': int(ntimesteps) + 1,
       'RightAscension': opts.rightascension,
       'Declination': '%s' % opts.declination,
       'AntennaTableName': opts.tblname,
       'MSName': msname,
       })
    if opts.debug:
        print(cfg_dict)

    # import sys
    # sys.exit(0)

    # generate a measurement set
    # http://stackoverflow.com/a/15343686
    with tempfile.NamedTemporaryFile(delete=False) as file:
        cfg_write_ms(file, cfg_dict, verbose=opts.debug)
    try:
        subprocess.check_call(['makems', file.name])
    except subprocess.CalledProcessError as e:
        # TODO: handle or report exception here, maybe
        pass
    finally:
        os.remove(file.name)
    # this is a lofar script and will use the position information, but loose the namings
    # so the original ANTENNA table needs to be copied back into the MS
    antenna_dir = '%s_p0/ANTENNA' % msname
    antenna_bak = antenna_dir + '.bak'  # this is at least '.bak'
    shutil.rmtree(antenna_bak, ignore_errors=True)  # /should/ be safe enough
    shutil.move(antenna_dir, antenna_bak)
    shutil.copytree(opts.tblname, antenna_dir)
    return '%s_p0' % msname


# -fin-
