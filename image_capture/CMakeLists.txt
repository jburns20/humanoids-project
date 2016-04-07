cmake_minimum_required (VERSION 2.8)
project (image_capture CXX)

CMAKE_POLICY( SET CMP0003 OLD )

set (CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake" )

# Add sources here... #
add_executable (image_capture image_capture.cpp)

# libpixyusb should always come before libboost and libusb #
target_link_libraries (image_capture pixyusb)

find_package ( libpixyusb REQUIRED )
find_package ( libusb-1.0 REQUIRED )
find_package ( Boost 1.49 COMPONENTS thread system chrono REQUIRED)
find_package ( Qt4 4.0.0 REQUIRED QtGui QtCore )

target_link_libraries (image_capture ${Boost_LIBRARIES})
target_link_libraries (image_capture ${LIBUSB_1_LIBRARY})
target_link_libraries (image_capture Qt4::QtGui Qt4::QtCore)


file(STRINGS "cmake/VERSION" LIBPIXY_VERSION)
add_definitions(-D__LIBPIXY_VERSION__="${LIBPIXY_VERSION}")

include_directories (src
                     include
                     ../../common
                     ${Boost_INCLUDE_DIR}
                     ${LIBUSB_1_INCLUDE_DIRS})

