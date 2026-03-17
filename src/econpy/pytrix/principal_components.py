import numpy as N

#%%%%%%%%%%%%%%%%%%%%%%%%%%%  Tomic code  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
class PCA:
	def __init__(self, inputMatrix, meancenter):
		"""
		This class carries out Principal Component Analysis on (numeric/numarray)
		matrices.
		
		use:
		analysis = PCA(Matrix, 0) / no mean centering of data
		analysis = PCA(Matrix, 1) / mean centering of data
		
		Matrix: array from package 'numeric'/'numarray'
		
		:author: Oliver Tomic
		:organization: Matforsk - Norwegian Food Research Institute
		:version: 1.0
		:since: 29.06.2005
		:see: Modular Data Toolkit for another implementation http://mdp-toolkit.sourceforge.net/
		:see: prepca from matplotlib.mlab (simpler implementation)
		"""
		
		from numpy.lib.mlab import svd, std, cov
		[numberOfObjects, numberOfVariables] = shape(inputMatrix)
		
		# This creates a matrix that keeps the original input matrix. That is
		# necessary, since 'inputMatrix' will be centered in the process and
		# the function GetCorrelationLoadings requires the original values.
		self.originalMatrix = zeros((numberOfObjects, numberOfVariables), float32)
		for rows in range(numberOfObjects):
			for cols in range(numberOfVariables):
				self.originalMatrix[rows, cols] = inputMatrix[rows, cols]
		
		# Meancenter inputMatrix if required
		if meancenter == 1:
			
			variableMean = average(inputMatrix, 0)
			
			for row in range(0, numberOfObjects):
				inputMatrix[row] = inputMatrix[row] - variableMean

		
		# Do the single value decomposition
		[U,S_values,V_trans] = svd(inputMatrix)

		S = zeros((len(S_values),len(S_values)), float32)
		for singVal in range(len(S_values)):
			S[singVal][singVal] = S_values[singVal]
		
		# Calculate scores (T) and loadings (P)
		self.scores = U*S_values
		self.loadings = transpose(V_trans)
		
		self.inputMatrix = inputMatrix
		
	def GetScores(self):
		"""
		Returns the score matrix T. First column is PC1, second is PC2, etc.
		"""
		return self.scores
	
	def GetLoadings(self):
		"""
		Returns the loading matrix P. First row is PC1, second is PC2, etc.
		"""
		return self.loadings
	
	def GetCorrelationLoadings(self):
		"""
		Returns the correlation loadings matrix based on T and inputMatrix.
		For variables in inputMatrix with std = 0, the value 0 is written
		in the correlation loadings matrix instead of 'Nan' as it should be
		(as for example in Matlab)
		""" 
		
		# Creates empty matrix for correlation loadings
		self.correlationLoadings = zeros((shape(self.scores)[1], shape(self.originalMatrix)[1]), float32)
		
		# Calculates correlation loadings with formula:
		# correlation = cov(x,y)/(std(x)*std(y))
		
		# For each PC in score matrix
		for PC in range(shape(self.scores)[1]):
			PCscores = self.scores[:, PC]
			PCscoresSTD = std(PCscores)
			
			# For each variable/attribute in original matrix (not meancentered)
			for var in range(shape(self.originalMatrix)[1]):
				origVar = self.originalMatrix[:, var]
				origVarSTD = std(origVar)
				
				# If std = 0 for any variable an OverflowError occurs.
				# In such a case the value 0 is written in the matrix
				try:
					self.correlationLoadings[PC, var] = cov(PCscores, origVar) / (PCscoresSTD * origVarSTD)
				
				except OverflowError:
					self.correlationLoadings[PC, var] = 0
		
		return self.correlationLoadings





#%%%%%%%%%%%%%%%%%%%%%%%%%%%  Pincus code  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def pca(data, algorithm='eig'):
	"""pca(data) -> mean, pcs, norm_pcs, variances, positions, norm_positions
	Perform Principal Components Analysis on a set of n data points in k
	dimensions. The data array must be of shape (n, k).
	This function returns the mean data point, the principal components (of
	shape (p, k), where p is the number pf principal components: p=min(n,k)),
	the normalized principal components, where each component is normalized by
	the data's standard deviation along that component (shape (p, k)), the
	variance each component represents (shape (p,)), the position of each data
	point along each component (shape (n, p)), and the position of each data
	point along each normalized component (shape (n, p)).
	
	The optional algorithm parameter can be either 'svd' to perform PCA with 
	the singular value decomposition, or 'eig' to use a symmetric eigenvalue
	decomposition. Empirically, eig is faster on the datasets I have tested.

	:license: public domain
	:author: Zachary Pincus <zpincus AT stanford DOT edu>
	"""
	
	data = N.asarray(data)
	mean = data.mean(axis = 0)
	centered = data - mean
	if algorithm=='eig':
		pcs, variances, stds, positions, norm_positions = _pca_eig(centered)  
	elif algorithm=='svd':
		pcs, variances, stds, positions, norm_positions = _pca_svd(centered)  
	else:
		raise RuntimeError('Algorithm %s not known.'%algorithm)
	norm_pcs = pcs * stds[:, N.newaxis]
	return mean, pcs, norm_pcs, variances, positions, norm_positions
	
def _pca_svd(data):
	u, s, vt = N.linalg.svd(data, full_matrices = 0)
	pcs = vt
	v = N.transpose(vt)
	data_count = len(flat)
	variances = s**2 / data_count
	root_data_count = N.sqrt(data_count)
	stds = s / root_data_count
	positions =  u * s
	norm_positions = u * root_data_count
	return pcs, variances, stds, positions, norm_positions

def _pca_eig(data):
	values, vectors = _symm_eig(data)
	pcs = vectors.transpose()
	variances = values / len(flat)
	stds = N.sqrt(variances)
	positions = N.dot(flat, vectors)
	err = N.seterr(divide='ignore', invalid='ignore')
	norm_positions = positions / stds
	N.seterr(**err)
	norm_positions[~N.isfinite(norm_positions)] = 0
	return pcs, variances, stds, positions, norm_positions

def _symm_eig(a):
	"""Return the eigenvectors and eigenvalues of the symmetric matrix a'a. If
	a has more columns than rows, then that matrix will be rank-deficient,
	and the non-zero eigenvalues and eigenvectors can be more easily extracted
	from the matrix aa'.
	From the properties of the SVD:
		if a of shape (m,n) has SVD u*s*v', then:
		  a'a = v*s's*v'
		  aa' = u*ss'*u'
		let s_hat, an array of shape (m,n), be such that s * s_hat = I(m,m) 
		and s_hat * s = I(n,n). (Note that s_hat is just the elementwise 
		reciprocal of s, as s is zero except on the main diagonal.)
		
		Thus, we can solve for u or v in terms of the other:
		  v = a'*u*s_hat'
		  u = a*v*s_hat      
	"""
	m, n = a.shape
	if m >= n:
		# just return the eigenvalues and eigenvectors of a'a
		vecs, vals = _eigh(N.dot(a.transpose(), a))
		vecs = N.where(vecs < 0, 0, vecs)
		return vecs, vals
	else:
		# figure out the eigenvalues and vectors based on aa', which is smaller
		sst_diag, u = _eigh(N.dot(a, a.transpose()))
		# in case due to numerical instabilities we have sst_diag < 0 anywhere, 
		# peg them to zero
		sst_diag = N.where(sst_diag < 0, 0, sst_diag)
		# now get the inverse square root of the diagonal, which will form the
		# main diagonal of s_hat
		err = N.seterr(divide='ignore', invalid='ignore')
		s_hat_diag = 1/N.sqrt(sst_diag)
		N.seterr(**err)
		s_hat_diag[~N.isfinite(s_hat_diag)] = 0
		# s_hat_diag is a list of length m, a'u is (n,m), so we can just use
		# numpy's broadcasting instead of matrix multiplication, and only create
		# the upper mxm block of a'u, since that's all we'll use anyway...
		v = N.dot(a.transpose(), u[:,:m]) * s_hat_diag
		return sst_diag, v

def _eigh(m):
	values, vectors = N.linalg.eigh(m)
	order = N.flipud(values.argsort())
	return values[order], vectors[:,order]

