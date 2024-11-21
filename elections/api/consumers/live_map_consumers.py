import json
from decimal import Decimal

from channels.db import database_sync_to_async


from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q




class LiveMapConsumers(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = None
        self.room_group_name = "live-map-room"
        self.user_id = None

        await self.accept()

    async def receive_json(self, content):
        command = content.get("command", None)
        user_id = content.get("user_id", None)
        data = content.get("data", None)

        try:
            if command == "get_live_map_data":
                await self.get_live_map_data()

            if command == "get_map_filter_data":
                await self.get_map_filter_data(data)

        except ClientError as e:
            await self.handle_client_error(e)
    async def get_live_map_data(self):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_live_map_data_data = await get_live_map_data()

        if get_live_map_data_data is not None:
            payload = json.loads(get_live_map_data_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "payload": payload,
                }
            )

            # Trigger the event on DataAdminDashboardConsumers
            await self.channel_layer.group_send(
                'map-data-stream',
                {
                    "type": "update_live_map_dashboard",
                }
            )
        else:
            raise ClientError(204, "Something went wrong retrieving the data.")

    async def update_map_dashboard(self, event):
        await self.get_live_map_data()

    async def get_map_filter_data(self, data):
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        get_map_filter_data_data = await get_map_filter_data(data)

        if get_map_filter_data_data is not None:
            payload = json.loads(get_map_filter_data_data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "payload": payload,
                }
            )

            # Trigger the event on DataAdminDashboardConsumers
            await self.channel_layer.group_send(
                'data-stream',
                {
                    "type": "update_dashboard",
                }
            )
        else:
            raise ClientError(204, "Something went wrong retrieving the data.")


    async def chat_message(self, event):
        await self.send_json(
            {
                "payload": event["payload"],
            },
        )

    async def disconnect(self, close_code):
        """
        Called when the WebSocket closes for any reason.
        """
        # leave the room
        try:
            if self.room_id is not None:
                await self.leave_room(self.room_id)
        except Exception:
            pass

    async def handle_client_error(self, e):
        """
        Called when a ClientError is raised.
        Sends error data to UI.
        """
        error_data = {}
        error_data['error'] = e.code
        if e.message:
            error_data['message'] = e.message
            await self.send_json(error_data)
        return


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)



@database_sync_to_async
def get_live_map_data():

    from django.contrib.auth import get_user_model
    
    from elections.api.serializers import ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer, PresidentialCandidateRegionalVoteSerializer

    from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote, ParliamentaryCandidateRegionalVote

    from ghana_decides_proj.exceptions import ClientError

    from regions.models import PollingStation, Region, RegionLayerCoordinate

    User = get_user_model()


    payload = {}
    data = {}


    election_year = 2024
    election_level = "Presidential"
    result_state = "General"
    region_name = "All Regions"

    display_names_list = []


    region_name = None
    constituency_name = None
    electoral_area_name = None
    polling_station_name = None


    region_geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }



    if result_state == "General":
        election_2024 = Election.objects.all().filter(year=election_year).first()

        general_prez_can_votes = ElectionPresidentialCandidate.objects.filter(election=election_2024).order_by("-total_votes")
        general_prez_can_votes_serializer = ElectionPresidentialCandidateSerializer(general_prez_can_votes, many=True)
        candidates = general_prez_can_votes_serializer.data

        regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024)

        regions_map_data = {}

        for entry in regional_prez_can_votes:
            region_name = entry.region.region_name
            region_id = entry.region.region_id
            prez_candidate = entry.prez_candidate
            prez_candidate_serialized = ElectionPresidentialCandidateSerializer(prez_candidate, many=False).data

            # Retrieve region coordinates
            region_coordinates = RegionLayerCoordinate.objects.filter(region=entry.region)
            coordinates = [{"lng": coord.lng, "lat": coord.lat} for coord in region_coordinates]

            candidate_info = {
                "region_id": region_id,
                "election_prez_id": prez_candidate_serialized['election_prez_id'],
                "party_id": prez_candidate_serialized['candidate']['party']['party_id'],
                "party_name": prez_candidate_serialized['candidate']['party']['party_full_name'],
                "party_color": prez_candidate_serialized['candidate']['party']['party_color'],
                "total_votes": entry.total_votes,
                "coordinates": coordinates
            }

            if region_name not in regions_map_data:
                regions_map_data[region_name] = candidate_info
            else:
                if candidate_info["total_votes"] > regions_map_data[region_name]["total_votes"]:
                    regions_map_data[region_name] = candidate_info

        # Map to the desired structure
        region_data_list = []

        for region_name, info in regions_map_data.items():
            coordinates = info["coordinates"]
            formatted_coordinates = [[coord["lng"], coord["lat"]] for coord in coordinates]

            region_data = {
                "type": "Feature",
                "properties": {
                    "region_id": info.get("region_id", ""),
                    # Assuming region_id can be added in the original data structure
                    "region_name": region_name,
                    "leading_color": info["party_color"]
                },
                "geometry": {
                    "coordinates": [formatted_coordinates],
                    "type": "Polygon"
                }
            }

            region_geojson_data['features'].append(region_data)

    if result_state == "General":
        data['region_name'] = "All Regions"
    if result_state == "Region":
        data['region_name'] = region_name
    elif result_state == "Constituency":
        data['region_name'] = constituency_name
    elif result_state == "Electoral Area":
        data['region_name'] = electoral_area_name
    elif result_state == "Polling Station":
        data['region_name'] = polling_station_name


    data['election_year'] = election_year
    data['election_level'] = election_level
    data['result_state'] = result_state
    data['candidates'] = candidates
    data['display_names_list'] = display_names_list
    data['region_geojson_data'] = region_geojson_data


    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload, cls=CustomJSONEncoder)



@database_sync_to_async
def get_map_filter_data(dataa):

    from django.contrib.auth import get_user_model

    from elections.api.serializers import ElectionPresidentialCandidateSerializer, \
    ElectionParliamentaryCandidateSerializer, PresidentialCandidatePollingStationVoteSerializer, \
    ParliamentaryCandidatePollingStationVoteSerializer, PresidentialCandidateRegionalVoteSerializer

    from elections.models import Election, ElectionPresidentialCandidate, PresidentialCandidatePollingStationVote, \
    PresidentialCandidateElectoralAreaVote, PresidentialCandidateConstituencyVote, PresidentialCandidateRegionalVote, \
    ElectionParliamentaryCandidate, ParliamentaryCandidatePollingStationVote, ParliamentaryCandidateRegionalVote

    from ghana_decides_proj.exceptions import ClientError

    from regions.models import PollingStation, Region, RegionLayerCoordinate

    User = get_user_model()

    payload = {}
    data = {}

    print("###Entry")
    print(dataa)



    election_year = dataa['election_year']
    election_level = dataa['election_level']
    result_state = dataa['result_state']
    region_name = dataa['region_name']
    parl_parties = {}
    candidates = []

    display_names_list = []

    region_geojson_data = {
        "type": "FeatureCollection",
        "features": []
    }


    #region_name = None
    #constituency_name = None
    #electoral_area_name = None
    #polling_station_name = None

    if result_state == "General":
        election_2024 = Election.objects.all().filter(year=election_year).first()

        if election_level == "Presidential":
            general_prez_can_votes = ElectionPresidentialCandidate.objects.filter(election=election_2024).order_by("-total_votes")
            general_prez_can_votes_serializer = ElectionPresidentialCandidateSerializer(general_prez_can_votes,
                                                                                         many=True)
            candidates = general_prez_can_votes_serializer.data

            regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024)

            regions_map_data = {}

            for entry in regional_prez_can_votes:
                region_name = entry.region.region_name
                region_id = entry.region.region_id
                prez_candidate = entry.prez_candidate
                prez_candidate_serialized = ElectionPresidentialCandidateSerializer(prez_candidate, many=False).data

                # Retrieve region coordinates
                region_coordinates = RegionLayerCoordinate.objects.filter(region=entry.region)
                coordinates = [{"lng": coord.lng, "lat": coord.lat} for coord in region_coordinates]

                candidate_info = {
                    "region_id": region_id,
                    "election_prez_id": prez_candidate_serialized['election_prez_id'],
                    "party_id": prez_candidate_serialized['candidate']['party']['party_id'],
                    "party_name": prez_candidate_serialized['candidate']['party']['party_full_name'],
                    "party_color": prez_candidate_serialized['candidate']['party']['party_color'],
                    "total_votes": entry.total_votes,
                    "coordinates": coordinates
                }

                if region_name not in regions_map_data:
                    regions_map_data[region_name] = candidate_info
                else:
                    if candidate_info["total_votes"] > regions_map_data[region_name]["total_votes"]:
                        regions_map_data[region_name] = candidate_info

            # Map to the desired structure
            region_data_list = []

            for region_name, info in regions_map_data.items():
                coordinates = info["coordinates"]
                formatted_coordinates = [[coord["lng"], coord["lat"]] for coord in coordinates]

                region_data = {
                    "type": "Feature",
                    "properties": {
                        "region_id": info.get("region_id", ""),
                        # Assuming region_id can be added in the original data structure
                        "region_name": region_name,
                        "leading_color": info["party_color"]
                    },
                    "geometry": {
                        "coordinates": [formatted_coordinates],
                        "type": "Polygon"
                    }
                }

                region_geojson_data['features'].append(region_data)

        if election_level == "Parliamentary":
            all_election_2024_presidential_candidates = ElectionPresidentialCandidate.objects.all().filter(
                election=election_2024).order_by("-total_votes")

            if all_election_2024_presidential_candidates:
                _first_presidential_candidate = all_election_2024_presidential_candidates[0]
                first_prez_party = _first_presidential_candidate.candidate.party


            ## First arliamentary
            first_prez_parl_can = (ElectionParliamentaryCandidate.objects
                                   .filter(election=election_2024)
                                   .filter(won=True)
                                   .filter(candidate__party=_first_presidential_candidate.candidate.party)
                                   .order_by('-created_at')
                                   )

            parl_party_1 = {
                "party_full_name": first_prez_party.party_full_name,
                "party_initial": first_prez_party.party_initial,
                "party_logo": first_prez_party.party_logo.url,
                "seats": len(first_prez_parl_can),
            }

            parl_parties["first_parl_party"] = parl_party_1

            ##### Second PARLIAMENTARY

            if len(all_election_2024_presidential_candidates) > 1:
                _second_presidential_candidate = all_election_2024_presidential_candidates[1]
                second_prez_party = _second_presidential_candidate.candidate.party

            second_prez_parl_can = (ElectionParliamentaryCandidate.objects
                                    .filter(election=election_2024)
                                    .filter(won=True)
                                    .filter(candidate__party=second_prez_party)
                                    .order_by('-created_at')
                                    )

            parl_party_2 = {
                "party_full_name": second_prez_party.party_full_name,
                "party_initial": second_prez_party.party_initial,
                "party_logo": second_prez_party.party_logo.url,
                "seats": len(second_prez_parl_can),
            }

            parl_parties["second_parl_party"] = parl_party_2

        data['region_name'] = "All Regions"


        #regions = Region.objects.all()
        regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024).order_by('-total_votes')
        #print('###################')
        #print('###################')
        #print(regional_prez_can_votes.region)
        ##for region in regions:
        #    print(region.region_name)
        #    display_names_list.append(region.region_name)
#
        #    coordinates = RegionLayerCoordinate.objects.filter(region=region)
        #    formatted_coordinates = [[coord.lng, coord.lat] for coord in coordinates]
        #    region_data = {
        #        "type": "Feature",
        #        "properties": {
        #            "region_id": region.region_id,
        #            "region_name": region.region_name,
        #            #"leading_color": "#0000FF"
        #            "leading_color": "#008000"
        #        },
        #        "geometry": {
        #            "coordinates": [
        #                formatted_coordinates
        #            ],
        #            "type": "Polygon"
        #        }
        #    }
        #    region_geojson_data["features"].append(region_data)



    elif  result_state == "Region":
        election_2024 = Election.objects.all().filter(year=election_year).first()
        # region = Region.objects.all().get(region_name=region_name)

        if election_level == "Presidential":
            regional_prez_can_votes = PresidentialCandidateRegionalVote.objects.filter(election=election_2024).filter(region__region_name=region_name).order_by('-total_votes')
            print("############33 REGG")
            print(regional_prez_can_votes)
            # region_name = regional_prez_can_votes.first().region.region_name
            regional_prez_can_votes_serializer = PresidentialCandidateRegionalVoteSerializer(regional_prez_can_votes,
                                                                                             many=True)
            candidates = regional_prez_can_votes_serializer.data


        data['region_name'] = region_name
        regions = Region.objects.all()
        for region in regions:
            display_names_list.append(region.region_name)

       
    #elif result_state == "Constituency":
    #    data['region_name'] = constituency_name
    #elif result_state == "Electoral Area":
    #    data['region_name'] = electoral_area_name
    #elif result_state == "Polling Station":
    #    data['region_name'] = polling_station_name


    data['election_year'] = election_year
    data['election_level'] = election_level
    data['result_state'] = result_state
    data['candidates'] = candidates
    data['parl_parties'] = parl_parties
    data['display_names_list'] = display_names_list
    #data['region_geojson_data'] = region_geojson_data




    payload['message'] = "Successful"
    payload['data'] = data

    return json.dumps(payload, cls=CustomJSONEncoder)



