#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>

int main(int argc, char **argv)
{
  cv::VideoCapture cap(0); // open the default camera
  if(argc==2)
  {
    cap.release();
    cap.open(atoi(argv[1]));
  }
  if(!cap.isOpened())  // check if we succeeded
  {
    std::cerr<<"no camera!"<<std::endl;
    return -1;
  }
  std::cerr<<"camera opened"<<std::endl;

  cv::namedWindow("camera",1);
  cv::namedWindow("gray",1);
  cv::Mat frame,gray;

  cap >> frame;
  for(;;)
  {
    cap >> frame; // get a new frame from camera
    cv::cvtColor(frame,gray,CV_BGR2GRAY);
    cv::imshow("camera", frame);
    cv::imshow("gray", gray);
    if(cv::waitKey(10) >= 0) break;
  }
  // the camera will be deinitialized automatically in VideoCapture destructor
  return 0;
}
