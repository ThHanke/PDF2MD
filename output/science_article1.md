Contents lists available at ScienceDirect Polymer Testing journal homepage: www.elsevier.com/locate/polytest

## Test Method

A camera-based strain measurement technique for elastomer tensile testing: Simulation and practical application to understand the strain dependent accuracy characteristics R. Schlegel*, T. Hanke, A. Krombholz Fraunhofer Institute for Mechanics of Materials IWM, Walter-Hülse-Str. 1, D-06120 Halle (Saale), Germany

## A R T I C L E I N F O A B S T R A C T

Article history:
Received 24 January 2015 Accepted 15 April 2015 Available online 29 April 2015
Keywords:
Optical strain measurement Mark-tracking technique Strain measurement accuracy Elastomer Tensile testing The present work investigates the precision characteristics of two optical strain measurement techniques applied to elastomers subjected to large deformations. The measurement approach is based on generating intensity profiles by using several horizontal image lines in the region of an optical marker to be detected. For detectability and accuracy reasons, these lines are combined using a rank (maximum) value filter and a moving average filter, while the calculation of the marker centers is carried out either geo- or gravimetrically. Based on simulated profiles, the first part of this work investigates the influence of method related parameters on the measurement precision obtained, expressed in terms of the root mean square error (rms). Further, it establishes model relations between most important image/profile parameters and rms. In the second part, experimental image data obtained during tensile testing of an elastomer sample is analyzed by i) applying the strain measurement technique, ii) determining experimental rms-values and iii) discussing them in comparison to values predicted by the rms-model of part one. It was found that, for the gravimetrical center calculation, rms strongly depends on the number of profile pixels which is caused by image noise. In the present approach, image noise was reduced by multiple image line fusion, which can be assumed to be in terms of computation effort more effective than averaging multiple images. The developed rms-models were found to represent the strain dependent decrease of accuracy efficiently up to high strains (e.g. 900%) under practical conditions. To obtain optimal measurement precision with the presented methods in practice, appropriate low marker detection threshold intensities of about 0.3gs (gs esignal intensity) and application of a single application cycle of the moving average filter were proved to yield optimal results. At high strains, the application of the rank filter in combination with a geometric center calculation results in best measurement precision, while the differences to the gravimetric method are less but its trend is comparable to the simulation.

© 2015 Elsevier Ltd. All rights reserved.

## 1. Introduction

Optical strain measuring techniques based on image evaluation are widely used in materials characterization
[1e4]. Their application offer a number of advantages in comparison to other techniques such as non-contact measurements, characterization of small samples, thin sheets, large strains or complex components (strain field). However, understanding the advantages and limitations in accuracy and robustness are important to obtain optimal measurement results in mechanical characterization of polymers.

Most significant in tensile testing of elastomers while measuring the strain optically is the constitution of the optical markers. Because stuck markers rotate on the samples, especially in the strain hardening region, and, therefore, give incorrect strain data, markers painted on the specimens are considered. They are found to be the better choice at high deformations because they deform simultaneously with the sample. By increasing elongation, however, the contrast between markers and their background becomes weak which is usually accompanied by a decrease in lateral accuracy, not quantified so far. Therefore, interactions between image quality, methods and method related parameters are essential to understand the strain dependence of accuracy for highly strained elastomers.

In the past, several works were published dealing with the improvement and understanding of different optical strain measuring techniques [5e9]. The variety of methods can be divided into three groups: i) methods based on tracking geometric objects, e.g. dots or elliptical shapes, ii) grid line methods and iii) methods based on digital image correlation. A tracking method was presented by G'Sell and Hivers, who calculated the centers of gravity of dots [10,11]. They used their strain measurement procedure to derive the material response within a very small representative volume element (RVE), and to keep the strain rate constant in this RVE. However, no information was given on the accuracy achieved. Bretagne developed a mark tracking technique for strain field and volume variation measurements and evaluated it, without pre-processing, by applying a low pass filter and with several bilinear interpolations of the image, depending on the mark diameter [12]. The obtained uncertainties were reported to be in the range of 0.2-0.25 px for mark diameters of 1 pixel and, typically, 0.025-0.05 pixel for diameters ranging from 4-16 pixel. A semi-automated image analysis technique was developed by Haynes and co-workers to measure the surface strain from a printed grid [13]. For this method, the measurement error was estimated to be ±1px at each edge. Because of profile spreading, if deformation is increasing, the strain error becomes smaller and it was reported that the marker contrast is reducing in the same direction. Starkova use a custom made camera based technique to obtain the volume strain of elastomers where larger strain value deviations are found at higher elongations [14].

A qualitative evaluation of the performance of video extensometry based on mark tracking in comparison to e.g. the Moir�e technique, holographic interferometry and image correlation is given by Sinn and co-workers [15].

They addressed three main advantages of mark tracking: i) it is fast (Only a small area around one point needs to be analyzed.), ii) the measurement arrangement is easy to use, not only under laboratory conditions, and iii) it is applicable to a wide range of specimens by changing the optical magnification. As a limitation, Sinn mentions the sample preparation, in particular the placement of the required amount of markers on the sample in such a way that its influence on the mechanical properties can be neglected. The mark tracking method developed by Rotinat was proved to yield high precision values, but its applicability was reported to be limited to strains of approximately 56%
[16]. He observed that accuracy depends on the pixel diameter of the markers.

In digital image correlation (DIC), a reference image is divided into small portions/facets which may partially overlap. From each facet, a grey value array is analyzed and correlated with all grey value arrays of the following images. The maximum of the calculated correlation result in each frame indicates the highest linearity between the current image facet and the reference facet and, therefore, coincides with the new position of the reference facet in the current image. The displacement is given by the "movement" of that facet with respect to the original one. Suitable interpolation of the correlation results allows subpixel accuracy [17,18]. Hoult evaluated the influence of outof-plane movement using the digital image correlation technique. He compared the deviation (accuracy) of the optical strains with that obtained by a strain gauge in the Mohr's circle, and showed that out-of-plane errors can be effectively reduced from about 100mε down to 5mε [19]. The maximum precision of DIC was given by Chevalier to be approximately 1/100 px [20].

When testing new algorithms, generation of synthetic images, which e.g. contain objects subjected to known deformations, is reported to be a useful procedure [21].

Koljonen, for example, presented a method to create synthetic images by artificially deforming real images with control of SNR, while Robinson predicted the performance limits of image registration techniques based on the mean square error and the Cramer-Rao inequality [21,22].

Apart from the errors originating from the specific evaluation approach, the signal-to-noise (SNR) ratio plays an important role. To decrease image noise, specific filters are available in literature [19,23e25]. Image noise belongs to that type of error that is caused by the sensor. The most significant are dark current noise and non-uniform sensor response. Davidson mentions that flat-field errors originate from variations of the charge collection efficiency and, for high energy radiation, from variations of the detector thickness [26]. To minimize such errors, the sensor response is measured under flat field conditions to calculate a gain map which is used for compensation later. Dark current errors originate from the noise which individual sensor elements generate without being exposed to irradiation [27]. Further, the lens system used influences image quality and measurement precision. In particular, lens distortion causes non-uniform geometric distortion in the images. In literature, several methods are presented for compensation [28e30]. The impact of such systematic strain errors is reported to depend on the strain level [31].

Considering them is of significant importance at micro strain level. Additionally, the optical transfer function of this lens system can be expected to smooth the intensity profile to some extent.

In the present work, synthetic marker intensity profiles with defined SNR and width are generated. After shifting these markers, their centers are calculated by two algorithms to establish relations between most important parameters, and to quantify the accuracy expressed in terms of the root mean square error. Maximum and average filters are implemented by using different image lines, which is faster than commonly used multiple image fusion. Further, the profile based approach to detect marker locations requires less computational effort in comparison to DIC.

## 2. Experimental 2.1. Profile Generation

To simulate multiple image line fusion, synthetic image intensity lines were generated and combined using either a rank value filter (maximum) or an average filter to form intensity profiles. In this study, inverted intensity profiles are used because it was considered more logical that the black marker (signal) has a higher intensity in comparison to the background. Three classes of parameters and/or methods were studied: i) parameters related to the marker
(marker signal intensity (gs), noise intensity (gn,0), marker width (wp)), ii) parameters and methods related to fusion of the synthetic image lines and processing of the profile
(number of profile lines (npl), application of a maximum rank value filter or an average filter, number of recursively applied cycles of a moving average filter nsmo) and iii)
methods related to the determination of the marker centre (geometric or gravimetric method).

Fig. 1a is a sketch of a marker and its corresponding intensity profile at the indicated profile line position.

Similar, approximately circular markers with diameters of about < 1 mm can be easily applied to small tensile test specimens (ISO 527-2/5B), which are typically 2 mm in width. This specimen type is favored if only few grams of polymer material is available.

The signal intensity gs is the difference between marker
(gm) and background (gb) intensity. The threshold intensity gthr is relevant for accurately detecting the marker and measuring its centre. Fig. 1b gives an overview on the profile generation and measuring procedures. For sub-pixel displacement of markers in the synthetic single intensity profiles, two profile series were constructed from a reference profile (Fig. 2a). In the shifted profile series, the markers are moved either 1 pixel (step size 0.01 px) in the positive and negative direction, respectively. The theoretical displacement resolution is limited by the signal intensity. The displacement on sub-pixel scale can be understood as a reduction of the intensity at one marker edge and an increase at that opposite. Therefore, the minimum shifting distance is 2/gs. Defined gaussian noise was added to the profiles to adjust the SNR [32]. Eq. 1 describes the relation of noise generation where gi is the initial intensity, ri are unique random numbers in the range
-1 <ri< 1 for the pixel i and bgr is the noise amplitude. The impact of noise on the profile is illustrated in Fig. 2b and c.

g¼1 1=3ri;g (1) gr;i ¼ gi þ bgr, X 3
The number of profile lines npl was simulated by generating npl random numbers (eq. 1) at the profile coordinate i. The applied filter type was taken into account by selecting either the maximum of these random numbers or calculating their average according eq. 2 and 3 [27,33].

gmax ¼ max � gi;j0…gi;jn � (2) gavg ¼ 1=ðjn � j0Þ Z gi;jd j (3)
In some cases, a smoothing or moving average filter with the filter kernel 3R ¼ [111]/3 was applied once or recursively along the x-direction of the profiles after image line fusion. The impact of smoothing is illustrated in Fig. 2d.

Note that the profile width is increasing by one pixel in positive and negative x-direction for each cycle the filter was applied. This broadening has to be considered, in particular in the case of the gravimetric calculation method described in the following section.

## 2.2. Measurement Of The Marker Position

Two algorithms were used to obtain the marker position: a) the calculation of the geometric marker centers by eq. 4, where at first the marker flanks xup and xdown are detected, and secondly the precision is improved by linear interpolation (eq. 5), and b) a calculation of the markers centers of gravity using eq. 6 (xi - position of the pixel i with the intensity g) [10].

xm;cgm ¼ 1=2, � xup þ xdown � (4) x* up=down ¼ � gthr � bup=down �� aup=down aup=down ¼ g � xup=down � � g � xup=down � 1 � bup=down ¼ g � xup=down � � aup=down,xup=down (5) xup�1 ðgðxiÞ � gbÞ (6) xup�1 ðgðxiÞ � gbÞxi xm;cgr ¼ X xdownþ1 , X xdownþ1
In the following, the indices cgm and cgr are used as abbreviations for the geometric (eq. 4) and the gravimetric
(eq. 6) centre calculation method, respectively. For cgm, a linear interpolation at the marker edges was applied according eq. 5. This linear interpolation was preferred to higher order interpolation because in practice the shape of the profile is unknown and the error invoked by this simplification occurs at both marker edges.

For both, cgm and cgr, the edge detection functionality was improved to detect markers at lower SNR-values. In practical application, every marker is captured twice where the first capturing is carried out based on gthr of the previous image to calculate gb, gm and gthr. The latter parameter is used to precisely detect the marker in the actual profile.

By this procedure, inaccuracies in gthr because of changing illuminations conditions are minimized as long as gs remains constant.

A systematic investigation of the achievable precision was carried out based on the rms error obtained after linear regression of marker position vs. image index data. The image index data is preferred to the true marker position i) because it is not relevant for rms whether the one or the other value is used and ii) because the true marker position is unknown in real tensile tests. By this, the influence of method related parameters i) profile width, ii) number of smoothing cycles applied to the profile, iii) threshold intensity, iv) number of image lines used to construct the profile, v) applied profile construction filter and vi) the SNR
where studied. Each rms-data point in the diagrams was obtained as an average of about 100 simulations of marker shifting series. All simulation routines were written in C (MinGW). The fits were carried out using the GNU Scientific Library (version 1.8). Diagrams were constructed using Gnuplot (version 4.6).

## 2.3. Practical Application In Tensile Testing

The presented methods were applied to images of a Kraton D1102 specimen (dumbbell shaped, ISO 527-2 type 5B) recorded during uniaxial extension. Two black ink markers were painted on the specimen at a distance of about 5 mm. The tensile test was carried out with a Zwick/
Roell Z020 universal testing machine. During this test, about
400 images of 1624�1234 pixel resolution were recorded with an Aramis system (GOM). Aramis was calibrated by the recommended standard procedure to compensate lens distortion. Positions vs. image index diagrams were used to evaluate the methods in practice. A polynomial function Dlpoly(t) of degree 5 was fitted to this data and subtracted from it. Plotting these results in distance Dl-Dlpoly(t) vs.

measured stretch lm ¼ l(t)/l0 (l(t) - marker distance at times t) diagrams enables a visual and also a quantitative evaluation of the data scattering. For the latter, linear fits were applied in typical l-intervals (e.g. l ¼ 1.0-1.2, 1.45-1.8, 2.4-
2.8) to obtain the corresponding experimental rms in this range of stretch. The rms values were plotted vs. the elongation and fitted with the rms(SNR(l))-models, which will be introduced in the following sections.

## 3. Results And Discussion 3.1. Investigations Of Profile Parameters On Rms Based On Synthetic Images

At first, the influence of the threshold intensity gthr on rms is investigated. Fig. 3a shows the rms results for gthr values ranging from 0.1 to 0.9gs. No influence of gthr on rms can be found for the cgr algorithm. Here, the magnitude of rms depends on whether the shifting interval matches to gs.

E.g. in the case of gs ¼ 100 counts and xshift ¼ 0.01px rms is zero, while this is not the case for e.g. gs ¼ 110 at an identical shifting interval.

In Fig. 3a, rms reveals a minimum for cgm at about 0.2
and 0.8gs. The large rms errors at small and high thresholds are due to the interpolation conditions at the marker borders (sharp intensity steps). Improvements can be achieved for cgm by applying a moving average filter to the profile, which is illustrated in Fig. 3b for profiles at SNR ¼ 20. There, the range of low rms becomes broader for the cgm calculation. Interestingly, a slight decrease of rms with increasing gthr is observed for cgr in Fig. 3b. However, under practical conditions, markers are more reliably captured at lower gthr.

The increase of rms at gthr > 0.75gs for cgr are most probable because of asymmetry in detecting the marker at higher thresholds. Note that the effect becomes more pronounced after smoothing the profile where the smaller middle part of the marker is captured only. This is not the case for sharp profiles, where a larger intensity difference between the marker and the background offers higher precision.

The influence of nsmo on rms is shown in Fig. 4. In fact, if marker broadening effected by smoothing is taken into account and noise-free profile are measured, the moving average filter has no effect on the precision of cgr, but a continuous increase is observed if random noise is added. For markers without noise detected with cgm, oscillations of rms are observed while applying the average filter recursively. This lies in the nature of this filter and the linear interpolation procedure [27]. The effect is less pronounced at SNR ¼ 20, where a minimum of rms is found after about one smoothing cycle. After the moving average filter is applied at least once, rms of cgm is always below that of cgr.

For cgr, the increase of rms may be explained because more random noise is mixed with the profile data.

The influence of the profile width wp on rms is shown in Fig. 5a, which gives an overview on the obtained results.

Because in the case of cgm only the marker edges are relevant, there is no observable influence of wp on rms. For cgr, however, a linear increase of rms for increasing profile width is found, which is due to the accumulation of noise intensity with increasing number of profile pixels. This increase can be characterized by the slope m and the intersection with the rms-axis n in eq. 7 and Fig. 5. m and n depend on SNR according to mðSNRÞ ¼ m0SNRam and nðSNRÞ ¼ n0SNRan. The values of these parameters are:
m0 ¼ 0.015, am ¼ �0.91 and n0 ¼ 0.64, an ¼ �0.86.

rmscgr � wp � ¼ mðSNRÞwp þ nðSNRÞ (7)
The normalized rmsnorm(npl) data is shown in Fig. 6. Its trend when applying the maximum filter can be described by eq. 8 with c0,max ¼ 0.94 and c1,max ¼ 0.004.

rmsnorm;max � npl � ¼ � c0;max ln � npl � þ 1 �� n expðc1;max,nplÞ pl (8) rmsnorm;avg � npl � ¼ 1 . ffiffiffiffiffiffi pnpl (9) For the average filter, an _rms_-decrease according to eq. 9 is observed [27]. It can be seen in Fig. 6 that, in-between 2-6 profile lines, averaging is more effectively reducing the random noise in comparison to the maximum filter. However, for averaging, the signal intensity halves with each additional line chosen if only one line contains the signal information. It is essential to mention that the loss of signal intensity is not compensated by similar or lower reduction of the noise, so that _SNR_ rather decreases. Further, _SNR_ differs across the profile for circular markers if all lines with signal intensity are merged to one profile. The decrease is most pronounced at the borders, because only few pixels contain signal information, and less pronounced in the middle region. Rectangular markers would be not affected by this problem. However, for applying them on the specimens more accuracy is required. Further, such variations in signal-to-noise ratio are not observed for the averaging of complete images where _SNR_ remains rather homogeneous. During this 
study, a reduction of rms from 0.042 to 0.026 (�38 % z 1/e)
pixel was achieved by averaging two synthetic image series with identical sub-pixel displacement but different noise at SNR ¼ 20. In contrast, the application of profile averaging based on the image lines of interest in one image only reduces image capturing and computation efforts. From the intersection between rmsnorm,max and rmsnorm,avg in Fig. 6
observed at about 7 profile lines, one may conclude that, for larger npl, the maximum filter also yields a lower rms for experimental images because of the higher SNR-values at the peak borders. This is not always correct under practical conditions because inhomogeneities of the paint affect local intensity maxima. It is impossible for this filter to compensate the random noise added to these maxima by pixels with lower signal intensity in the surrounding area.

Because rms decreases with increasing numbers of profile lines (eq. 8 and 9), it should be reasonable to conclude that gn for the maximum filter and for the average filter show similar behavior (gn,max/avg(npl) ¼ gn,0 rmsnorm,-
max/avg(npl)). By considering this, SNR can now be described by eq. 10.

$$\text{SNR}(n_{pl})=g_{s}\Big{/}g_{n,max/avg}\left(n_{pl}\right)\tag{10}$$

Combining eq. 7 and 10 yields the following expression for $rms_{cgr}$

$$\text{rms}_{cgr,max/avg}=m_{0}\left(\frac{g_{s}}{g_{n,max/avg}\left(n_{pl}\right)}\right)^{a_{w}}W_{p}$$ $$+n_{0}\left(\frac{g_{s}}{g_{n,max/avg}\left(n_{pl}\right)}\right)^{a_{e}}\tag{11}$$

For cgm, less complex correlations were found where, as shown in Fig. 7a, rms decreases linearly on log-scale. This correlation can be described by eq. 12.

$$\text{rms}_{cgrm}(\text{SNR})=d_{1}/\text{SNR}\tag{12}$$
with d1 ~ 1.

Inserting eq. 10 into eq. 12 gives the root-mean-square error for the geometrical method in eq. 13 for the average and the maximum filter.

$$\text{rms}_{\text{gm},\text{max}/\text{avg}}(\text{SNR})=\text{rms}_{\text{m}\text{m}\text{m},\text{max}/\text{avg}}\left(n_{\text{pi}}\right)\cdot\text{g}_{\text{n},0}/\text{g}_{\text{s}}\tag{13}$$

Fig. 7a show that the $\text{rms}_{\text{g}\text{gm}}$ data for 1 and 12 profile lines is in good agreement with eq. 13 if smoothing was applied. Fig. 7b shows the $\text{rms}$ data and the model curves for cgr, which similarly decreases on log-scale with increasing $\text{SNR}$. A comparison between $\text{rms}_{\text{m}\text{m}\text{m}\text{m}}(\text{g}_{\text{s}})$, which is 
2/gs, and rms(SNR) makes clear that at high signal intensities the governing factor on the precision is SNR rather than gs. The equations derived so far will be applied to model profiles without fitting next.

Fig. 8 shows the obtained rms data and the corresponding model curves based on the parameters used during the profile construction. Stretch was taken into account by introducing profile broadening according to wp(l) ¼ lwp,0
and the intensity reduction according to eq. 14.

$$\mathbf{g}_{s}(\lambda)=\mathbf{g}_{s,0}/\lambda^{0.5}\tag{14}$$

This decrease of intensity was assumed to correlate with the reduction in thickness, which can be expressed in terms of the incompressibility relation for uniaxial tension: $\lambda_{1}\lambda_{2}\lambda_{3}=1$; $\lambda_{1}=\lambda_{2}$, $\lambda_{2}=\lambda_{3}=\lambda_{1}^{0.5}$. The diagrams in Fig. 8 verify that the models predict the synthetic _rms_ data sufficiently. At $n_{pl}=3$ a reduction of _rms_ can be observed for averaged profiles in comparison to the profiles to which the maximum filter was applied. Due to the accumulation of noise intensity, the _rms_ data achieved with cgr are usually higher in comparison to values obtained with cgm. From
the data shown in Fig. 8, better performance of the cgm e method is expected at high strains while, for small deformations, the cgr-method will be the better choice. A more detailed discussion of how far these simulation based results are transferable to practical applications will be the subject of the following section.

## 3.2. Practical Application In Tensile Testing

Sample images of one marker on the elastomer sample subjected to deformation are shown in Fig. 9aed. These images correspond to 0, 303, 491 and 662% strain, respectively. In Fig. 9, it can be seen that the marker extends parallel and contracts perpendicular to the direction of deformation. Fig. 10aed illustrates the marker extension based on the intensity profiles.

The contraction of the marker results in a reduction of the number of profile lines. Because for the elastomer the incompressibility relation holds, the decrease of the number of profile lines with relevant signal information during elongation should be described by eq. 15

nplðlÞ ¼ npl;0
         .
            ffiffiffi
            l
          p
                                          (15)

where npl,0 is the number of profile lines with signal in-
tensity of the undeformed sample. This value can be ob-
tained from the first image or calculated from the marker
intensity decrease, as shown later. While for the unde-
formed markers in Fig. 9a several vertical pixels can be
used to calculate the corresponding profile point at the
border, few or only one pixel line are available at higher
strains, as shown in Fig. 9bed. This implies that the
contraction of the marker affects a remarkable signal

decrease by using the average filter if the number of selected profile lines ($n_{pl,slct}$) is kept constant. This can be described by eq. 16.

$$g_{s,\,\rm{mg}}(\lambda)=1/n_{pl,slct}\int g_{s}(\lambda)d(n_{pl}(\lambda))\tag{16}$$

Eq. 16 simplifies to $g_{s,\,\rm{avg}}(\lambda)=(n_{pl,0}/n_{pl,slct})(g_{s,0}/\lambda)$ if the marker profile has a rectangular shape. Further, Fig. 10a-d reveals a pronounced decrease of marker signal intensity and a reduction of intensity homogeneity of the marker. The latter is caused by the property of the specific marker paint or the surface properties of the samples, e.g. higher brittleness due to thermal degradation.

Fig. 11 shows the measured intensity decrease as a function of the experimental stretch lm. The data points were fitted to eq. 14 for the maximum filter and the simplified eq. 16 for the average filter. For the maximum filter, gs,max,0 was treated as a free fitting parameter and it was kept constant for the average filter. The k-parameter, which represents the ratio npl,0/npl,slct, was freely variable.

gs,max,0 ¼ 87 px and k ¼ 0.74 were obtained by fitting, which are reasonable values (npl,slct ¼ 10, npl,0 ¼ 7.4 pixel). This value is in agreement with Fig. 9a if the marker height is measured manually. Finally, it becomes clear that the model curve of the average filter describes the experimental data sufficiently without further fitting.

Fig.12 shows the strain vs. time (l-t-) curve of the image series obtained with cgm and a maximum filter with npl ¼ 20. In this diagram, the positions of the images and the profiles depicted in Figs. 9 and 10 are indicated. The initially obtained Dlm vs. t curves were fitted by the polynomial Dlpoly(t) of order N ¼ 5, which was subtracted from the data resulting the plot in Fig. 12a. Experimental rms values were obtained by applying linear fits in specific small l-ranges, which again were plotted vs. the average l in each range (Fig. 13a). To characterize the performance of the investigated methods, the minimum rms value at small strains (rmsmin) and the slope z ¼ Drms/Dl was obtained from these diagrams. Table 1 and 2 are giving an overview on these parameters at 30 and 50 % threshold intensity, respectively. The data shows that the application of the moving average filter improves accuracy. In Table 1 and 2 it can be seen that cgr produces larger slope values in comparison to cgm, which is in principle in agreement with the simulation results. For cgr, a combination with the average filter shows better performance at small strains compared to the maximum filter, while for cgm it is the maximum filter which yields more accurate data. The smallest rms values observed at small strains are about 0.03 px, which was obtained with the cgr-method. This method is recommended for applications to achieve high accuracy in the lower strain regions. However, the slope is almost twice that of that observed for cgm so that, for large deformations, cgm-max(nsmo ¼ 1) with its still relatively small rmsmin is the better choice.

It can be concluded from Table 2 that lowering the threshold is significantly reducing rmsmin and z. However, reducing gthr greatly effects interaction with the marker background, which again increases rms. At gthr ¼ 0.3gs,max cgr-avg(nsmo ¼ 1) is still the best choice for higher precision at low strains, while at high strains either cgmmax(nsmo ¼ 1) or cgr-max(nsmo ¼ 1) are recommended.

In the following, the rms(l)-model will be proved under practical conditions. At first the image parameters gs,0 and gn are determined. gn,0 was obtained from the background intensity noise by evaluating the intensity of a background pixel at constant coordinates through the entire image series. It was found to be about 5.6 px. Note that this value is not identical to the image noise of the camera. gs,0 was taken from Fig. 11. As a last parameter npl,0 was obtained from Fig. 11 by fitting the gs(l)-data of the average filter by using the parameter npl,slct ¼ 10.

Fig. 13a and b show the experimentally determined rms data of cgr-max and cgr-avg. The measurements of the marker positions were carried out with and without profile smoothing and at two different threshold intensities, respectively. The model curves were not fitted to the experimental data, but npl,0 was set to 7.4. For the maximum filter (Fig. 13a and c) it was assumed that, in principle, only a few profile lines with the highest intensity at the middle of the marker are relevant, so that npl,0 was fixed at 2 here. For smaller npl,0 values, the curve shifts to higher rms values. The best agreement between model and experimental data can be found at low strains, for smoothed profiles and at low thresholds. It is assumed that most of the marker is captured at a lower intensity threshold. Similar good agreement between model and experimental data can be found for cgr-avg in Fig. 13b.

Again, low threshold intensities and application of one running average filter cycle to the profile yields the lowest rms at high strains. For the average filter (Fig. 13b and d), the rms(l)-curve is slightly above the minimum rms-data obtained experimentally. This indicates an assumed higher noise level in the model or a more pronounced decrease of npl(l) in the model in comparison to the experimental data.

For cgm, the model curves are again in best agreement to experimental rms-data obtained at low threshold intensities.

This can be understood considering the intensity difference between neighboring pixels at the marker edge. These large gradients in gs were found to cause pronounced interpolation errors during shifting synthetic markers. By applying a running average filter, the intensity steps at the border become smaller and this decreases the observed error.

## 4. Conclusions

Two optical strain measurement techniques for elastomer samples with painted markers were characterized with respect to their accuracy in detecting sub-pixel displacement. For that, intensity profiles were generated

Method
z [px/l]
rmsmin [px]
Method
z [px/l]
rmsmin [px]
cgm-avg (nsmo ¼ 0)
0.052
0.149
cgm-avg (nsmo ¼ 1)
0.059
0.101
cgr-avg (nsmo ¼ 0)
0.140
0.056
cgr-avg (nsmo ¼ 1)
0.102
0.030
cgm-max (nsmo ¼ 0)
0.057
0.072
cgm-max (nsmo ¼ 1)
0.025
0.073
cgr-max (nsmo ¼ 0)
0.138
0.062
cgr-max (nsmo ¼ 1)
0.044
0.055
cgm-avg (nsmo ¼ 0)
0.048
0.066
cgm-avg (nsmo ¼ 1)
0.038
0.042
cgr-avg (nsmo ¼ 0)
0.103
0.037
cgr-avg (nsmo ¼ 1)
0.070
0.030
cgm-max (nsmo ¼ 0)
0.022
0.010
cgm-max (nsmo ¼ 1)
0.018
0.056
cgr-max (nsmo ¼ 0)
0.027
0.066
cgr-max (nsmo ¼ 1)
0.021
0.050

and shifted on sub-pixel scale. The distances between synthetic markers were determined by locating their geometric or gravimetric centre. The resulting distances vs. image index curves were fitted to obtain a root-mean-square error.

For both the geometric and the gravimetric method, the influence of the filter (maximum and average) to construct the profile, the profile width, the number of smoothing cycles (application of an additional running average filter along the profile), the threshold intensity at which the marker were detected, the number of image lines used to construct the profile and the signal-to-noise ratio (SNR) was studied. Model equations were deduced to describe the influence of rms as a function of relevant parameters and, finally, the stretch l. SNR was found to be the most significant factor for both methods, while the second is either the profile width (gravimetric method) or the intensity differences at the marker edges (geometric method). Profile smoothing additionally increases the accuracy for the geometric method. The obtained model equations describe sufficiently well the rms(l) trend of synthetic profiles. In a second step, geometric and gravimetric methods were applied to experimental images recorded during an elastomer tensile test. In this case, minimum rms values of about 0.03 px at low strains and a minimum increase of about 0.02
px/l were found. Under practical conditions, low intensity thresholds were observed to yield higher accuracy.

Simulation and experimental data revealed that the gravimetric method (cgr) is most suitable for small deformations, while the geometric method(cgm) should be preferentially used at larger strains. The transition point for switching from cgr to cgm can be estimated by the model equations derived in this study and the image parameters.

This investigation should enable users of optical strain measurement techniques in industry or laboratory research to optimize their experimental conditions and to predict the possible accuracy in terms of the root-mean-square error. The proposed profile based methods serve as fast and easy to apply routines, which are suitable for detecting large deformations.

## Acknowledgements

This work was initiated and motivated within an internal program of the Fraunhofer IWM to which the authors acknowledge for financial support in the early stage of this research. Parts of this research were carried out in a period funded by the German Science Foundation (DFG, WE 2272/ 12-1) to which R. Schlegel would like to acknowledge. We would like to thank our colleagues for helpful discussions.

## References

[1] B.K. Satapathy, R. Lach, R. Weidisch, K. Schneider, A. Janke, K. Knoll,
Copolymer/homopolymer
blends,
Eng.
Fract.Mech.
73
(2006)
2399e2412.
[2] F. Grytten, H. Daiyan, M. Polanco-Loria, S. Dumoulin, Use of digital
image correlation to measure large-strain tensile properties of ductile thermoplastics, Polym.Test. 28 (2009) 653e660.
[3] T. G�omez del Río, A. Salazar, J. Rodríguez, Effect of strain rate and
temperature on tensile properties of ethyleneepropylene block
copolymers, J. Mater. and Des. 42 (2012) 301e307.
[4] R. Schlegel, Y.X. Duan, R. Weidisch, S. H€olzer, K. Schneider,
M. Stamm, D. Uhrig, J.W. Mays, G. Heinrich, N. Hadjichristidis, Highstrain-induced deformation mechanisms in blockgraft and multigraft copolymers, Macromol. 44 (2011) 9374e9383.
[5] S.C.N. T€opfer, G. Linß, Quality measures for optical probing in optical
coordinate metrology, Measurement Sci. Rev. 7 (4) (2007) 51e54.
[6] P.C. Bastias, S.M. Kulkari, K.-Y. Kim, J. Gargas, Noncontacting strain
measurements during tensile tests, Exp. Mech. 36 (1996) 78e83.
[7] C.A. Sciammarella, Overview of optical techniques that measure
displacements: Murray Lecture, Exp. Mech. 43 (2003) 1e19.
[8] M. Tourlonias, M.-A. Bueno, L. Bigu�e, B. Durand, M. Renner, Contactless optical extensometer for textile materials, Exp. Mech. 45
(2005) 420e426.
[9] M. Bornert, F. Br�emand, P. Doumalin, J.-C. Dupr�e, M. Fazzini,
M. Gr�ediac, F. Hild, S. Mistou, J. Molimard, J.-J. Orteu, Assessment of digital image correlation measurement errors: methodology and results, Exp. Mech. 49 (2009) 353e370.
[10] C. G'Sell, J.M. Hiver, A. Dahoun, Experimental characterization of
deformation damage in solid polymers under tension, and its interrelation with necking, Int. J. Solids and Struct. 39 (2002) 3857e3872.
[11] F. Addiego, A. Dahoun, C. G'Sell, J.M. Hiver, Characterization of
volume strain at large deformation under uniaxial tension in highdensity polyethylene, Polym. 47 (2006) 4387e4399.
[12] N. Bretagne, V. Valle, J.C. Dupr�e, Development of the mark tracking
technique for strain field and volume variation measurements,
NDT&E Int. 38 (2005) 290e298.
[13] A.R. Haynes, P.D. Coates, Semi-automated image analysis of the true
tensile drawing behaviour of polymers to large strains, J. Mater. Sci. 31 (1996) 1843e1855.
[14] O. Starkova, A. Aniskevich, Poisson's ratio and the incompressibility
relation for various strain measures with the example of a silica-filled
SBR rubber in uniaxial tension tests, Polym. Test. 29 (2010) 310e318.
[15] G. Sinn, A. Reiterer, S. Stanzl-Tschegg, E.K. Tschegg, Determination
of strains of thin wood samples using videoextensometry, Holz als Roh- und Werkst. 59 (2001) 177e182.
[16] R. Rotinat, R. Ti�e bi, V. Valle, J.-C. Dupr�e, Three optical procedures for
local large-strain measurement, Strain 37 (3) (2001) 89e98.
[17] R. Meier, et al. (Eds.), Proceedings of the 35th IEEE PVSC Honolulo,
2010.
[18] E. Parson, M.C. Boyce, D.M. Parks, An experimental investigation of
the large-strain tensile behavior of neat and rubber-toughened polycarbonate, Polym. 45 (2004) 2665e2684.
[19] N.A. Hoult, W.A. Take, C. Lee, M. Dutton, Experimental accuracy of
two dimensional strain measurements using digital image correlation, Eng. Struct. 46 (2013) 718e726.
[20] L. Chevalier, S. Calloch, F. Hild, Y. Marco, Digital image correlation
used to analyze the multiaxial behavior of rubber-like materials, Eur. J. Mech. A/Solids 20 (2001) 169e187.
[21] J. Koljonen, J.T. Alander, Deformation image generation for testing a
strain measurement algorithm, Opt. Eng. 47 (10) (2010) 107202.
[22] D. Robinson, P. Milanfar, Fundamental performance limits in image
registration, IEEE Transactions on Image Proc. 13 (9) (2004) 1185e1199.
[23] A. Bijaoui, Y. Bobichon, B. Vandame, Multiscale image fusion in astronomy, Vistas in Astron. 41 (3) (1997) 365e372.
[24] M.-H. Hsieh, F.-C. Cheng, M.-C. Shie, S.-J. Ruan, Fast and efficient
median filter for removing 1e99% levels of salt-and-pepper noise in
images, Eng. Appl. Artif. Intell. 26 (2013) 1333e1338.
[25] C.-L. Lin, C.-W. Kuo, C.-C. Lai, M.-D. Tsai, Y.-C. Chang, H.-Y. Cheng, A
novel approach to fast noise reduction of infrared image, Infrared
Phys. & Technol. 54 (2011) 1e9.
[26] D.W. Davidson, C. Fr€ojdh, V. O'Shea, H.-E. Nilsson, M. Rahman, Limitations to flat field correction methods when using an X-ray spectrum, Nucl. Instrum. and Methods in Phys. Res. A 509 (2003) 146e150.
[27] B. J€ahne, Digitale Bildverarbeitung, 7. Auflage, Springer Vieweg, 2012.
[28] J.S. Sirkis, T.J. Lim, Displacement and strain measurement with
automated grid methods, Exp. Mech. 31 (4) (1991) 382e388.
[29] B. Pan, L. Yu, D. Wu, L. Tang, Systematic errors in two dimensional
digital image correlation due to lens distortion, Optics. & Lasers. in Eng. 51 (2013) 140e147.
[30] J. Sun, X. Chen, Z. Gong, Z. Liu, Y. Zhao, Accurate camera calibration
with distortion models using sphere images, Optics. & Laser.
Technol. 65 (2015) 83e87.
[31] P. Lava, W. van Paepegem, S. Coppieters, I. De Baere, Y. Wang,
D. Debruyne, Impact of lens distrortions on strain measurements obtained with 2D digital image correlation, Optics. & Lasers. in Eng. 51 (2013) 576e585.
[32] D.Ch. von Grünigen, Digitale Signalverarbeitung, 5. Auflage, Fachbuchverlag Leipzig, 2014.
[33] G. Heygster, Rank filters in digital image processing, Comp. Graphics
and Image Process. 19 (1982) 148e164.