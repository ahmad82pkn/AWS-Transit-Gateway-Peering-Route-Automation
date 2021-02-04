#!/usr/bin/python

import json
import boto3
import time

def get_difference(CurrentPeeringRoutes, ListOfRoutesInTGWBRtb):
    return set(CurrentPeeringRoutes)-set(ListOfRoutesInTGWBRtb)

########HOW TO USE#######
### Update Region and TGW Route table ID in both dict_1 and dict_2 and then run it
### Please test in non prod enviroment
dict_1={'eu-west-1':'tgw-rtb-02f0332eff36798b8','us-east-1':'tgw-rtb-06f193a6844ee6ecb','ap-southeast-2':'tgw-rtb-0c8625479f0113972','ap-southeast-1':'tgw-rtb-0f10a46df9436b682'}
dict_2={'eu-west-1':'tgw-rtb-02f0332eff36798b8','us-east-1':'tgw-rtb-06f193a6844ee6ecb','ap-southeast-2':'tgw-rtb-0c8625479f0113972','ap-southeast-1':'tgw-rtb-0f10a46df9436b682'}
###############Outer Loop Dict1##########
for region1 in dict_1:

    
###############Inner Loop Dict2##########    
    for region2 in dict_2:
        if region2==region1:
#            print("Source and destination Regions are same, skipping route checks")
            continue
        tgwclient1 = boto3.client('ec2',region_name=region1)
        tgwclient2 = boto3.client('ec2',region_name=region2)
##############
        print("printing dict2[region2] " +dict_2[region2])
        
        
        get_tgw_id1=tgwclient1.describe_transit_gateway_route_tables(
            TransitGatewayRouteTableIds=[
                            dict_1[region1],
                        ],
                        )
        tgwid1=get_tgw_id1['TransitGatewayRouteTables'][0]['TransitGatewayId']
        print(tgwid1)

        
        get_tgw_id2=tgwclient2.describe_transit_gateway_route_tables(
            TransitGatewayRouteTableIds=[
                            dict_2[region2],
                        ],
                        )
        tgwid2=get_tgw_id2['TransitGatewayRouteTables'][0]['TransitGatewayId']
        print(tgwid2)
##############Describe all peering attachments for each Dict_1 regions#######
        findattachment=tgwclient2.describe_transit_gateway_peering_attachments(
                    Filters=[
                        {
                            'Name': 'state',
                            'Values': [
                                'available',
                                        ]
                        },
                            ],
                                )
        for i in findattachment['TransitGatewayPeeringAttachments']:
            if ((i['RequesterTgwInfo']['TransitGatewayId']==tgwid1 or i['AccepterTgwInfo']['TransitGatewayId']==tgwid1) and (i['RequesterTgwInfo']['TransitGatewayId']==tgwid2 or i['AccepterTgwInfo']['TransitGatewayId']==tgwid2)):
                print("Peering session found between below regions")
                print(i['RequesterTgwInfo']['Region'])
                print(i['AccepterTgwInfo']['Region'])        
                print("Peering attachment ID "+i['TransitGatewayAttachmentId'])
                tgwsearch1=tgwclient1.search_transit_gateway_routes(
                    TransitGatewayRouteTableId=dict_1[region1],
                    Filters=[
                        {
                            'Name':'attachment.transit-gateway-attachment-id',
                            'Values':[
                                    i['TransitGatewayAttachmentId'],
                                    ]
                        },
                        ],
                )

                ListOfRoutesInPeeringRtb=[]
                for eachroute in tgwsearch1['Routes']:
                    ListOfRoutesInPeeringRtb.append(eachroute['DestinationCidrBlock'])
                print("Current Peering Routes in "+region1 +" towards destination region "+region2+ " peering are")
                print(ListOfRoutesInPeeringRtb)
                ListOfRoutesInTGWBRtb = []
############Grep routes from remote TGW Region 2 from Dict_2 if they are propagated from VPC###############
                tgwsearch2=tgwclient2.search_transit_gateway_routes(
                TransitGatewayRouteTableId=dict_2[region2],
                Filters=[
                        {
                                'Name':'type',
                                'Values':[
                                        'propagated',
                                        ]
                        },
                        ],
            )
                for eachroute in tgwsearch2['Routes']:
                    if eachroute['TransitGatewayAttachments'][0]['ResourceType'] == 'vpc':
#                        route = str(eachroute['DestinationCidrBlock'])
                        ListOfRoutesInTGWBRtb.append(eachroute['DestinationCidrBlock'])
                print("Remote region "+region2+" Route Table LIST:")
                print(ListOfRoutesInTGWBRtb)


##Extra Routes in Current Peering Routes in Region 1 that needs to be removed##


                non_match = list(get_difference(ListOfRoutesInPeeringRtb, ListOfRoutesInTGWBRtb))

                if non_match:
                    print("Extra Routes in "+dict_1[region1]+"  dict1-vpc with next hop Peering that needs to be removed, as Remote TGW dont have such Propagated VPC routes")
                    print(non_match)
                    for MissingRoute in non_match:
                        tgwclient1.delete_transit_gateway_route(
                        DestinationCidrBlock=MissingRoute,
                        TransitGatewayRouteTableId=dict_1[region1]
                        )
                else:
                    print("No Extra Route in "+dict_1[region1]+"  Current Peering that needs to be removed")


##Extra VPC Route in remote Region 2 RTB that should be added in Region 1 TGW Route table pointing to Peering as Next hop##
                ExtraRouteinTGWRTB=list(set(ListOfRoutesInTGWBRtb)-set(ListOfRoutesInPeeringRtb))
                if ExtraRouteinTGWRTB:
                    print("Peering route table "+dict_1[region1]+"   is missing below VPC routes that are present in remote TGW Route table "+dict_2[region2]+", Need to add below extra routes")
                    print(ExtraRouteinTGWRTB)
                    for eachExtraRoute in ExtraRouteinTGWRTB:
                        tgwclient1.create_transit_gateway_route(
                            DestinationCidrBlock=eachExtraRoute,
                            TransitGatewayRouteTableId=dict_1[region1],
                            TransitGatewayAttachmentId=i['TransitGatewayAttachmentId'])
                else:
                    print("Peering route table "+dict_1[region1]+" is not missing any routes in Peering that needs to be added")

