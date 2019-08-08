"""
Tests for tobac based on simple sample datasets with moving blobs. These tests should be adapted to be more modular in the future.
"""
from tobac.testing import make_sample_data_2D_3blobs, make_sample_data_2D_3blobs_inv
from tobac import feature_detection_multithreshold,linking_trackpy,get_spacings
from iris.analysis import MEAN,MAX,MIN
from pandas.testing import assert_frame_equal
from numpy.testing import assert_allclose

def test_sample_data():
    """
    Test to make sure that sample datasets in the following tests are set up the right way
    """
    sample_data=make_sample_data_2D_3blobs()
    sample_data_inv=make_sample_data_2D_3blobs_inv()
    
    assert sample_data.coord('projection_x_coordinate')==sample_data_inv.coord('projection_x_coordinate')
    assert sample_data.coord('projection_y_coordinate')==sample_data_inv.coord('projection_y_coordinate')
    assert sample_data.coord('time')==sample_data_inv.coord('time')
    minimum=sample_data.collapsed(('time','projection_x_coordinate','projection_y_coordinate'),MIN).data
    minimum_inv=sample_data_inv.collapsed(('time','projection_x_coordinate','projection_y_coordinate'),MIN).data
    assert_allclose(minimum,minimum_inv)
    mean=sample_data.collapsed(('time','projection_x_coordinate','projection_y_coordinate'),MEAN).data
    mean_inv=sample_data_inv.collapsed(('time','projection_x_coordinate','projection_y_coordinate'),MEAN).data
    assert_allclose(mean,mean_inv)

def test_tracking_coord_order():
    """
    Test a tracking applications to make sure that coordinate order does not lead to different results
    """
    sample_data=make_sample_data_2D_3blobs()
    sample_data_inv=make_sample_data_2D_3blobs_inv()
    # Keyword arguments for feature detection step:
    parameters_features={}
    parameters_features['position_threshold']='weighted_diff'
    parameters_features['sigma_threshold']=0.5
    parameters_features['min_num']=3
    parameters_features['min_distance']=0
    parameters_features['sigma_threshold']=1
    parameters_features['threshold']=[3,5,10] #m/s
    parameters_features['n_erosion_threshold']=0
    parameters_features['n_min_threshold']=3
    
    #calculate  dxy,dt
    dxy,dt=get_spacings(sample_data)
    dxy_inv,dt_inv=get_spacings(sample_data_inv)

    #Test that dt and dxy are the same for different order of coordinates
    assert_allclose(dxy,dxy_inv)
    assert_allclose(dt,dt_inv)
    
    #Test that dt and dxy are as expected
    assert_allclose(dt,60)
    assert_allclose(dxy,1000)
     
    #Find features
    Features=feature_detection_multithreshold(sample_data,dxy,**parameters_features)
    Features_inv=feature_detection_multithreshold(sample_data_inv,dxy_inv,**parameters_features)

    parameters_linking={}
    parameters_linking['method_linking']='predict'
    parameters_linking['adaptive_stop']=0.2
    parameters_linking['adaptive_step']=0.95
    parameters_linking['extrapolate']=0
    parameters_linking['order']=1
    parameters_linking['subnetwork_size']=100
    parameters_linking['memory']=0
    parameters_linking['time_cell_min']=5*60
    parameters_linking['method_linking']='predict'
    parameters_linking['v_max']=100
    parameters_linking['d_min']=2000
    
    Track=linking_trackpy(Features,sample_data,dt=dt,dxy=dxy,**parameters_linking)
    Track_inv=linking_trackpy(Features_inv,sample_data_inv,dt=dt_inv,dxy=dxy_inv,**parameters_linking)