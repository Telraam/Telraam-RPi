# Telraam

**Telraam is an affordable and yet intricate traffic-monitoring network built around a cluster of low-cost sensors and a central server. It is a collaboration between [Transport & Mobility Leuven (TML)](https://www.tmleuven.be/en/), [Mobiel 21](https://www.mobiel21.be/) en [Waanz.in](https://waanz.in/) that is financed by the Smart Mobility Belgium Grant of the Federal Government.**

Precisely measured traffic volumes are essential for transport-related studies. Within the Telraam-project, we develop an integrated application based on low-cost hardware, a central database and processing server, and a public online platform allowing citizens to contibute to automated real-time traffic counts.

:runner::bike::blue_car::truck:

Pedestrians, cyclists, cars, and heavy vehicles are each counted separately when passing in front of the low-resolution camera (without actual images being stored). The resulting traffic data can be used to perform traffic engeneering studies. This way, citizens and citizen platforms get objective data, allowing them to engage in a dialogue based on actual data with their local government. This could result in actions such as for instance a modification of the driving direction, the redesign of the public space, an improvent of the cycling conditions, or a modification of the parking infrastructure.

TML develops the architecture, the hardware setup and the software for the sensor, and uses the resulting traffic count data in a pilot case in [Kessel-Lo](https://www.google.com/maps/place/Kessel-Lo,+3010+Leuven/) (Leuven, Belgium) to showcase the possibilities of the application to both citizens as well as local governments.

In the pilot case in Kessel-Lo, we roll out a local network of 100 counting points. Furthermore, we provide 100 additional sensors to set up small networks in other places accross Flanders. 

By the end of this project, we expect the number of sensors to grow organically beyond the original volume, and that independent applications emerge that make use of the traffic count data.

For more information (in Dutch) and the live traffic map, please visit the [Terlaam website](https://telraam.net/).

## Telraam on the Raspberry Pi

In this repository we make the script that runs on the Rapsberry Pi computers at each Telraam user available to the public. The goal of this - besides being completely transparent and honest about our methods - is to provide an opportunity to the public to improve upon (parts) of the original script developed at Transport & Mobility Leuven (TML, Belgium), and help the Telraam network reach its maximum potential. Please make sure to observe our CC BY-SA license.

Below you will find a list of dependencies that are needed for the script to run, a link to a detailed documentation that explains some ideas behind the script in a more detailed way than how it is done by comments placed inside the script itself, and a list of developement goals that we would like the community to pay special attention to.

#### Dependencies

...

#### Detailed documentation

...

#### Developement goals

- [ ] Advanced (Bayesian) tracking
- [ ] Compressed data transfer to the server
- [ ] ...
