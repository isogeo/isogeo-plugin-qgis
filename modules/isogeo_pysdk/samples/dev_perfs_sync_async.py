# -*- coding: UTF-8 -*-
#! python3

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import asyncio
from concurrent.futures import ThreadPoolExecutor
from os import environ
from timeit import default_timer

# Isogeo
from isogeo_pysdk import Isogeo

# #############################################################################
# ######## Globals #################
# ##################################

# API access
app_id = environ.get("ISOGEO_API_DEV_ID")
app_token = environ.get("ISOGEO_API_DEV_SECRET")

# start Isogeo
isogeo = Isogeo(client_id=app_id, client_secret=app_token)

# getting a token
token = isogeo.connect()


# #############################################################################
# ########## Functions ##############
# ##################################
def _meta_get_resource_sync(md_uuid):
    """Just a meta func to get execution time"""
    isogeo.resource(id_resource=md_uuid)

    elapsed = default_timer() - START_TIME
    time_completed_at = "{:5.2f}s".format(elapsed)
    print("{0:<30} {1:>20}".format(md_uuid, time_completed_at))

    return


# ASYNC
async def get_data_asynchronous():
    with ThreadPoolExecutor(max_workers=5, thread_name_prefix="IsogeoApi") as executor:
        # Set any session parameters here before calling `fetch`
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                _meta_get_resource_sync,
                # Allows us to pass in multiple arguments to `fetch`
                *(md_uuid,),
            )
            for md_uuid in md_ids
        ]

        # store responses
        out_list = []
        for response in await asyncio.gather(*tasks):
            out_list.append(response)

        return out_list


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    how_much_mds = 100

    # get the metadata ids
    md_ids = [
        md.get("_id")
        for md in isogeo.search(page_size=how_much_mds, whole_share=0).get("results")
    ]

    # SYNC
    print("Get {} complete metadata - SYNCHRONOUS MODE".format(how_much_mds))
    print("{0:<30} {1:>20}".format("File", "Completed at"))

    # SYNCHRONOUS
    total_start_time = default_timer()
    for md_uuid in md_ids:
        isogeo.resource(id_resource=md_uuid)
        elapsed = default_timer() - total_start_time
        time_completed_at = "{:5.2f}s".format(elapsed)
        print("{0:<30} {1:>20}".format(md_uuid, time_completed_at))

    elapsed = default_timer() - total_start_time
    time_completed_at = "{:5.2f}s".format(elapsed)
    print("SYNCHRONOUS - TOTAL ELAPSED TIME: " + time_completed_at)

    # ASYNC
    print("\nGet {} complete metadata - ASYNCHRONOUS MODE".format(how_much_mds))
    START_TIME = default_timer()
    print("{0:<30} {1:>20}".format("File", "Completed at"))
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous())
    loop.run_until_complete(future)

    elapsed = default_timer() - START_TIME
    time_completed_at = "{:5.2f}s".format(elapsed)
    print("{} metadatas retrieved.".format(len(future.result())))
    print("ASYNCHRONOUS - TOTAL ELAPSED TIME: " + time_completed_at)
