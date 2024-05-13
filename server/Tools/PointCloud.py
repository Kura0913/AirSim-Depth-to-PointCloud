import numpy as np
from scipy.spatial import cKDTree


class PointCloud:
    # import AirSim lidar's data of cloud points, shape the data to (x, y, z) format
    def parse_point_cloud(self, point_ary):
        x_points = []
        y_points = []
        z_points = []

        for i in range(0, point_ary.shape[0], 3):
            x_points.append(point_ary[i])
            y_points.append(point_ary[i+1])
            z_points.append(point_ary[i+2])

        return x_points, y_points, z_points
    
    def circle_touching_point(self, point, cloud_points_dict, r):
        '''
        Check if the point is close to our known point cloud
        '''
        center_point = np.array(point)
        points = np.array(list(cloud_points_dict.values()))

        # Create KD-Tree
        kdtree = cKDTree(points)
        close_points_indices = kdtree.query_ball_point(center_point, r)
        if len(close_points_indices) > 0:
            return True
        else:
            return False    
    