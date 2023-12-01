# mat1i labels;
# int n_labels = connectedcomponents(img, labels);

# for (int i = 1; i < n_labels; ++i)
# {
#     // get the mask for the i-th contour
#     mat1b mask_i = labels == i;

#     // compute the contour
#     vector<vector<point>> contours;     
#     findcontours(mask_i.clone(), contours, retr_external, chain_approx_none);

#     if (!contours.empty())
#     {
#         // the first contour (and probably the only one)
#         // is the one you're looking for

#         // compute the perimeter
#         double perimeter_i = contours[0].size();
#     }
# }

# //getting the connected components with statistics
# cv::mat1i labels, stats;
# cv::mat centroids;

# int lab = connectedcomponentswithstats(img, labels, stats, centroids);

# for (int i = 1; i < lab; ++i)
# {
#     //rectangle around the connected component
#     cv::rect rect(stats(i, 0), stats(i, 1), stats(i, 2), stats(i, 3));

#     // get the mask for the i-th contour
#     mat1b mask_i = labels(rect) == i;

#     // compute the contour
#     vector<vector<point>> contours;     
#     findcontours(mask_i, contours, retr_external, chain_approx_none);

#     if(contours.size() <= 0)
#          continue;        

#     //finding the perimeter
#     double perimeter = contours[0].size();
#     //you can use this as well for measuring perimeter
#     //double perimeter = arclength(contours[0], true);

# }