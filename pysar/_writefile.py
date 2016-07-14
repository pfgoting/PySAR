############################################################
# Program is part of PySAR v1.0                            #
# Copyright(c) 2013, Heresh Fattahi                        #
# Author:  Heresh Fattahi                                  #
############################################################
#
# Yunjun, Sep 2015: Add write_gamma_float() and write_gamma_scomplex()
# Yunjun, Oct 2015: Add support for write_float32(amp, phase, outname)
# Yunjun, Jan 2016: Add write()


import os
import numpy as np


#def write_float32(data,outname):
def write_float32(*args):
   # To write an array to a binary file with float32 precision
   # Format of the binary file is same as roi_pac unw, cor, or hgt data.
   # Exmaple:
   #         write_float32(phase, outname)
   #         write_float32(amp, phase, outname)

   if len(args)==2:
      amp     = args[0]
      pha     = args[0]
      outname = args[1]
   elif len(args)==3:
      amp     = args[0]
      pha     = args[1]
      outname = args[2]
   else:
      print 'Error while getting args: support 2/3 args only.'
      return

   nlines = pha.shape[0]
   WIDTH  = pha.shape[1]
   F=np.zeros([2*nlines*WIDTH,1],np.float32)

   for line in range(nlines):
       F[(2*WIDTH)*(line) :       (2*WIDTH)*(line)+WIDTH]=np.reshape(amp[line][:],[WIDTH,1])
       F[(2*WIDTH)*(line)+WIDTH : (2*WIDTH)*(line+1)]    =np.reshape(pha[line][:],[WIDTH,1])

   F.tofile(outname)


def write_complex64(data,outname):   
   # writes roi_pac .int data
   nlines=data.shape[0]
   WIDTH=data.shape[1]
   R=np.cos(data)
   Im=np.sin(data)
   # F=np.zeros([2*nlines*WIDTH,1],np.complex64) 
   F=np.zeros([2*nlines*WIDTH,1],np.float32)  
   id1=range(0,2*nlines*WIDTH,2)
   id2=range(1,2*nlines*WIDTH,2)
   F[id1]=np.reshape(R,(nlines*WIDTH,1))
   F[id2]=np.reshape(Im,(nlines*WIDTH,1))
   F.tofile(outname)


def write_dem(data,outname):
   data=np.array(data,dtype=np.int16)
   data.tofile(outname)


def write_gamma_float(data,outname):
   ## write gamma float data, i.e. .mli file.
   data=np.array(data,dtype=np.float32)
   data.tofile(outname)


def write_gamma_scomplex(data,outname):
   ## write gamma scomplex data, i.e. .slc file.
   ## data is complex 2-D matrix
   nlines = data.shape[0]
   WIDTH  = data.shape[1]
   id1 = range(0,2*nlines*WIDTH,2)
   id2 = range(1,2*nlines*WIDTH,2)
   F=np.zeros([2*nlines*WIDTH,1],np.int16)
   F[id1]=np.reshape(data.real,(nlines*WIDTH,1))
   F[id2]=np.reshape(data.imag,(nlines*WIDTH,1))
   F.tofile(outname)


def write(*args):
  ## Write one dataset, i.e. interferogram, coherence, velocity, dem ...
  ##     return 0 if failed.

  ## Usage:
  ##     write(data,atr,outname)
  ##     write(rg,az,atr,outname)
  ##
  ##   Inputs:
  ##     data : 2D data matrix
  ##     atr  : attribute object
  ##     outname : output file name

  ## Examples:
  ##     write(data,atr,'velocity.h5')
  ##     write(data,atr,'temporal_coherence.h5')
  ##
  ##     write(data,atr,'100120-110214.unw')
  ##     write(data,atr,'strm1.dem')
  ##     write(data,atr,'100120.mli')
  ##     write(rg,az,atr,'geomap_4lks.trans')


  ########## Check Inputs ##########
  if len(args) == 4:       ## .trans file
      rg      = args[0]
      az      = args[1]
      atr     = args[2]
      outname = args[3]
  else:
      data    = args[0]
      atr     = args[1]
      outname = args[2]

  type      = atr['FILE_TYPE']
  ext = os.path.splitext(outname)[1].lower()
  ############### Read ###############
  print 'writing >>> '+outname
  ##### PySAR HDF5 product
  if ext == '.h5':
      if type in ['interferograms','coherence','wrapped','timeseries']:
          print 'Un-supported file type: '+type
          print 'Only support 1-dataset-1-attribute file, i.e. velocity, mask, ...'
          return 0;
      import h5py
      h5file = h5py.File(outname,'w')
      group = h5file.create_group(type)
      dset = group.create_dataset(type, data=data, compression='gzip')
      for key , value in atr.iteritems():    group.attrs[key]=value
      h5file.close()

      return 1;

  ##### ISCE / ROI_PAC GAMMA / Image product
  else:
      ##### Write Data File
      if   type in ['.unw','.cor','.hgt']:
          write_float32(data,outname)
      elif type == '.dem':
          write_dem(data,outname)
      elif type == '.trans':
          write_float32(rg,az,outname)
      elif type in ['.jpeg','.jpg','.png','.ras','.bmp']:
          import Image
          data.save(outname)
      elif type == '.mli':
          write_gamma_float(data,outname)
      elif type == '.slc':
          write_gamma_scomplex(data,outname)
      else: print 'Un-supported file type: '+type; return 0;

      ##### Write .rsc File
      f = open(outname+'.rsc','w')
      for key in atr.keys():    f.write(key+'    '+atr[key]+'\n')
      f.close()

      return 1;
