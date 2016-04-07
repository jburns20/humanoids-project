#include "opencv2/core/core.hpp"
#include "opencv2/calib3d/calib3d.hpp"
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <cstdio>
#include <iostream>
#include <fstream>

using namespace cv;
using namespace std;


int main() {
  Mat img1, img2;
  img1 = imread("images/left6.jpg", 0);
  img2 = imread("images/right6.jpg", 0);

  Size img_size = img1.size();

  int SADWindowSize = 0;

  int numberOfDisparities = 0;
  numberOfDisparities = 128; //numberOfDisparities > 0 ? numberOfDisparities : ((img_size.width/8) + 15) & -16;

  Ptr<StereoSGBM> sgbm = StereoSGBM::create(0,16,3);

  sgbm->setPreFilterCap(63);

  int sgbmWinSize = SADWindowSize > 0 ? SADWindowSize : 3;
  sgbm->setBlockSize(sgbmWinSize);

  int cn = img1.channels();

  sgbm->setP1(8*cn*sgbmWinSize*sgbmWinSize);
  sgbm->setP2(32*cn*sgbmWinSize*sgbmWinSize);
  sgbm->setMinDisparity(-64);
  sgbm->setNumDisparities(numberOfDisparities);
  sgbm->setUniquenessRatio(10);
  sgbm->setSpeckleWindowSize(100);
  sgbm->setSpeckleRange(32);
  sgbm->setDisp12MaxDiff(1);

  sgbm->setMode(StereoSGBM::MODE_HH);

  Mat disp, disp8;

  int64 t = getTickCount();
  sgbm->compute(img1, img2, disp);
  t = getTickCount() - t;
  printf("Time elapsed: %fms\n", t*1000/getTickFrequency());

  disp.convertTo(disp8, CV_8U, 255/(numberOfDisparities*16.));

  imwrite("images/better-output6.jpg", disp8);


}