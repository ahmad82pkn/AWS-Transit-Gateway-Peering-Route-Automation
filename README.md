# AWS-Transit-Gateway-Peering-Route-Automation
AWS TGW Transit Gateway peering Route Automation

########HOW TO USE#######
### Update Region and TGW Route table ID in both dict_1 and dict_2 and then run it
### Please test in non prod enviroment first, as I tried to tackle most of the scenarios but some exceptions may be remaining.
### Any suggestions are welcome


=================

As we know, TGW peering need static routes to be added in each TGW for remote VPC's CIDR.

In future AWS may release BGP/propagation support in TGW peering, but right now its manual process.  



You can run this code on demand or cron job with lambda with every 30 minutes ( or time you choose, lets say your dev ops attach VPC and detach them on their own development cycle and you can give them ETA of 10 or 20 minutes that after that time routing will be available etc )

This code will gather all VPC propagated routes from Peered TGW and update each TGW respective attachment ID and make sure there is full routing available between all peered TGW.

###################

Points to note.

1-This code only runs in same account , that is all TGW should be in same account. In next iteration, I am planning to add cross account support. 

2- This code works with default RTB with default setting that has VPC propagation enabled ( non default RTB can be used as long as VPC propagation is enabled) It will not work with more than 1 RTB, so VPC propagated routes and VPC peering route table should be same ( In summary all attachment VPC and PEERING must be in same RTB).

3- I have successfully tested it with 4 TGW in 4 regions connected with each other fully and partially with default route table in each TGW.



Pre Req and How to use the Code.

1- TGW peering should exist before running the code.

2- There are two dictionaries in the Code

Dict_1 and Dict_2

Populate these dictionaries with your own TGW region and default RTB ID



Code attached
