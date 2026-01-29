#!/usr/bin/env python3
import rospy
import tf
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped

def path_publisher():
    rospy.init_node('rovio_path_node')

    parent_frame = rospy.get_param('~parent_frame_id', 'world')
    child_frame = rospy.get_param('~child_frame_id', 'imu')
    out_topic = rospy.get_param('~out_topic', '/my_path')

    listener = tf.TransformListener()
    path_pub = rospy.Publisher(out_topic, Path, queue_size=10)
    
    path = Path()
    path.header.frame_id = parent_frame

    rate = rospy.Rate(10)
    
    rospy.loginfo(f"Starting path tracking: {parent_frame} -> {child_frame}")

    while not rospy.is_shutdown():
        try:
            now = rospy.Time(0) 
            listener.waitForTransform(parent_frame, child_frame, now, rospy.Duration(0.1))
            
            (trans, rot) = listener.lookupTransform(parent_frame, child_frame, now)

            pose = PoseStamped()
            pose.header.stamp = rospy.Time.now()
            pose.header.frame_id = parent_frame
            pose.pose.position.x = trans[0]
            pose.pose.position.y = trans[1]
            pose.pose.position.z = trans[2]
            pose.pose.orientation.x = rot[0]
            pose.pose.orientation.y = rot[1]
            pose.pose.orientation.z = rot[2]
            pose.pose.orientation.w = rot[3]

            path.poses.append(pose)
            path.header.stamp = rospy.Time.now()
            path_pub.publish(path)

        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException) as e:
            rospy.logwarn_throttle(5, f"Still waiting for transform: {e}")
            continue
            
        rate.sleep()

if __name__ == '__main__':
    try:
        path_publisher()
    except rospy.ROSInterruptException:
        pass
