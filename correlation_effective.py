import matplotlib.pyplot as plt
import numpy as np
import green as g
import source as s
import processing as proc
import parameters
import time

def correlation_effective(rec0=0,rec1=1,verbose=0,plot=0,save=0):

	"""
	cct_eff,t,ccf_eff,f = correlation_effective(rec0=0,rec1=1,verbose=0,plot=0,save=0)

	Compute the effective correlation function for receiver pair rec0-rec1. This requires
	the following previous steps:

	(i) Run correlation_random to compute and store individual correlations for each time window.
	(ii) Run correction_factors to compute and store source and propagation correctors.

	INPUT:
	------
	rec0, rec1:		indeces of the receivers used in the correlation. 
	plot:			plot when 1.
	verbose:		give screen output when 1.
	save:			store frequency-domain effective correlation to OUTPUT/correlations

	OUTPUT:
	-------
	cct_eff, t:		Time-domain effective correlation function and time axis [T]*[N^2 s / m^4],[s].
	ccf_eff, f:		Frequency-domain correlation function and frequency axis [T]*[N^2 s^2 / m^4],[1/s].
	
	Last updated: 13 March 2016.
	"""

	#==============================================================================
	#- Initialisation.
	#==============================================================================

	#- Basic input. ---------------------------------------------------------------

	p=parameters.Parameters()

	#- Load frequency and time axes. ----------------------------------------------

	fn='OUTPUT/correlations_individual/f'
	fid=open(fn,'r')
	f=np.load(fid)
	fid.close()

	fn='OUTPUT/correlations_individual/t'
	fid=open(fn,'r')
	t=np.load(fid)
	fid.close()

	#- Read raw and processed individual correlations. ----------------------------

	fn='OUTPUT/correlations_individual/ccf_'+str(rec0)+'_'+str(rec1)
	fid=open(fn,'r')
	ccf=np.load(fid)
	fid.close()

	fn='OUTPUT/correlations_individual/ccf_proc_'+str(rec0)+'_'+str(rec1)
	fid=open(fn,'r')
	ccf_proc=np.load(fid)
	fid.close()

	#- Load frequency-domain propagation corrector. -------------------------------

	fn='OUTPUT/correctors/g_'+str(rec0)+'_'+str(rec1)
	fid=open(fn,'r')
	gf=np.load(fid)
	fid.close()

	#==============================================================================
	#- March through the individual time windows.
	#==============================================================================

	ccf_eff=np.zeros(len(f),dtype=complex)

	for k in range(p.Nwindows):

		#- Load frequency-domain source corrector. --------------------------------

		fn='OUTPUT/correctors/'+str(k)+'_f'
		fid=open(fn,'r')
		nff=np.load(fid)
		fid.close()

		#- Compute this time-window contribution to the effective correlation. ----

		ccf_eff+=ccf[:,k]*nff*gf

	#- Normalise. -----------------------------------------------------------------

	ccf_eff=ccf_eff/p.Nwindows

	#==============================================================================
	#- Compute ensembles and time-domain representations.
	#==============================================================================

	n=len(t)

	cct_raw=np.zeros(n,dtype=float)
	cct_eff=np.zeros(n,dtype=float)
	cct_proc=np.zeros(n,dtype=float)

	ccf_raw_ensemble=np.sum(ccf,axis=1)/p.Nwindows
	ccf_proc_ensemble=np.sum(ccf_proc,axis=1)/p.Nwindows

	#print np.shape(ccf_raw_ensemble)

	dummy=np.real(np.fft.ifft(ccf_raw_ensemble)/p.dt)
	cct_raw[0.5*n:n]=dummy[0:0.5*n]
	cct_raw[0:0.5*n]=dummy[0.5*n:n]

	dummy=np.real(np.fft.ifft(ccf_proc_ensemble)/p.dt)
	cct_proc[0.5*n:n]=dummy[0:0.5*n]
	cct_proc[0:0.5*n]=dummy[0.5*n:n]

	dummy=np.real(np.fft.ifft(ccf_eff)/p.dt)
	cct_eff[0.5*n:n]=dummy[0:0.5*n]
	cct_eff[0:0.5*n]=dummy[0.5*n:n]

	#==============================================================================
	#- Save results if wanted.
	#==============================================================================

	if save==1:

		#- Store effective correlations in the frequency domain.

		fn='OUTPUT/correlations/ccf_eff_'+str(rec0)+'_'+str(rec1)
		fid=open(fn,'w')
		np.save(fid,ccf_eff)
		fid.close()


	#==============================================================================
	#- Plot if wanted.
	#==============================================================================

	if plot==1:

		#- Processed and effective ensemble correlations. 
		
		plt.plot(f,np.abs(ccf_proc_ensemble),'k')
		plt.plot(f,np.abs(ccf_eff),'r')
		plt.title('ensemble frequency-domain correlation (black=processed, red=effective)')
		plt.ylabel('correlation [N^2 s^2 / m^4]*unit(T)')
		plt.xlabel('f [Hz]')

		plt.show()

		plt.plot(t,cct_proc,'k')
		plt.plot(t,cct_eff,'r')
		plt.title('ensemble time-domain correlation (black=processed, red=effective)')
		plt.ylabel('correlation [N^2 s / m^4]*unit(T)')
		plt.xlabel('t [s]')

		plt.show()

	#==============================================================================
	#- Return.
	#==============================================================================

	return cct_eff,t,ccf_eff,f