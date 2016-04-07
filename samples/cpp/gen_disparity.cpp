/* compile with g++ `pkg-config --cflags --libs opencv` gen_disparity.cpp -o gendisp */


#include "opencv2/calib3d/calib3d.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/imgcodecs.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/core/utility.hpp"

#include <stdio.h>

using namespace cv;

int main() {
  Ptr<StereoBM> bm = StereoBM::create(16,9);
  std::string img1_filename = "images/left6.jpg";
  std::string img2_filename = "images/right6.jpg";

  int SADWindowSize, numDisparities;

  Mat img1 = imread(img1_filename, 0);
  Mat img2 = imread(img2_filename, 0);

  Size img_size = img1.size();

  numDisparities = ((img_size.width/8) + 15) & -16;

  bm->setPreFilterCap(31);
  bm->setBlockSize(SADWindowSize > 0 ? SADWindowSize : 9);
  bm->setMinDisparity(0);
  bm->setNumDisparities(numDisparities);
  bm->setTextureThreshold(10);
  bm->setUniquenessRatio(15);
  bm->setSpeckleWindowSize(100);
  bm->setSpeckleRange(32);
  bm->setDisp12MaxDiff(1);

  Mat disp, disp8;
  int64 t = getTickCount();

  bm->compute(img1, img2, disp);
  t = getTickCount() - t;
  printf("Time elapsed: %fms\n", t*1000/getTickFrequency());

  disp.convertTo(disp8, CV_8U);
  imwrite("images/output6.jpg", disp8);

  //Ptr<StereoSGBM> sgbm = StereoSGBM::create(0,16,3);

}
