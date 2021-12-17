import os
from functools import partial 
from datetime import timedelta
from functools import reduce

from shapely.geometry import Point, LineString, Polygon, MultiPoint
import numpy as np

from aisdb import zones_dir, output_dir
from aisdb.gis import Domain, ZoneGeomFromTxt
from aisdb.track_gen import trackgen, segment_tracks_timesplits, fence_tracks, max_tracklength, segment_tracks_encode_greatcircledistance, concat_realisticspeed, mmsifilter, mmsirange
from aisdb.network_graph import serialize_network_edge
from aisdb.proc_util import deserialize_generator
from aisdb.track_viz import TrackViz



keyorder = lambda key: int(key.rsplit(os.path.sep, 1)[1].split('.')[0].split('Z')[1])
shapefilepaths = sorted(reduce(np.append, 
    [list(map(os.path.join, (path[0] for p in path[2]), path[2])) for path in list(os.walk(zones_dir))]
    ), key=keyorder)
zonegeoms = {z.name : z for z in [ZoneGeomFromTxt(f) for f in shapefilepaths]} 
#domain = Domain('west', {k:v for k,v in zonegeoms.items() if 'WZ' in k}, clearcache=True)
domain = Domain('east', {k:v for k,v in zonegeoms.items() if 'EZ' in k}, clearcache=True)

viz = TrackViz()
for txt, geom in list(domain.geoms.items()):
	viz.add_feature_poly(geom.geometry, ident=txt, opacity=0.3, color=(200, 200, 200))


fpath = os.path.join(output_dir, 'rowgen_year_test2.pickle')


timesplit = partial(segment_tracks_timesplits,  maxdelta=timedelta(hours=28))
distsplit = partial(segment_tracks_encode_greatcircledistance, maxdistance=100000, cuttime=timedelta(hours=28), cutknots=50, minscore=0.000005) 
geofenced = partial(fence_tracks,               domain=domain)
serialize = partial(serialize_network_edge,     domain=domain)


viz.clear_lines()
viz.clear_points()
#testmmsi = [218158000, 316043424, 316015104]
testmmsi = [218158000, 316001088, 316043424, 316015104]
rowgen = deserialize_generator(fpath)

#tracks = max_tracklength(trackgen(mmsifilter(rowgen, mmsis=testmmsi)))
tracks = distsplit(timesplit(trackgen(mmsifilter(rowgen, mmsis=testmmsi))))


n = 0
for track in tracks:
    if len(track['time']) < 1:
        assert False
    elif len(track['time']) == 1:
        ptgeom = MultiPoint([Point(x,y) for x,y in zip(track['lon'], track['lat'])])
        viz.add_feature_point(ptgeom, ident=track['mmsi']+1000)
    else:
        linegeom = LineString(zip(track['lon'], track['lat']))
        viz.add_feature_line(linegeom, ident=track['mmsi']+1000)
    n += 1
    print(f'{n}')
viz.focus_canvas_item(domain=domain)

viz.render_vectors()


exit()


from aisdb.track_viz import processing
processing.algorithmHelp('qgis:union')

params = {
        #'INPUT': self.basemap_lyr,
        'INPUT': vl3,
        'OVERLAY': vl3,
        'OUTPUT': os.path.join(output_dir, 'testimg.png'),
    }
feedback = QgsProcessingFeedback()

res = processing.run('qgis:union', params, feedback=feedback)

from qgis.core import QgsLabelPosition, QgsProcessingFeedback


'''
notable changes:
    split on speed>50knots, rejoined using distance+time score
        - has weird effects at boundary of domain, probably doesnt affect zone crossings though
    in cases where scores tie, last one is picked instead of first one
    changed score datatype to 16-bit float (lower precision means more ties, causing it to prefer more recent tracks)
    corrected indexing error when computing scores
    took the average of 2 nearest scores instead of single score
    
    tested minimum score 
'''


from aisdb.merge_data import merge_tracks_hullgeom, merge_tracks_shoredist, merge_tracks_bathymetry
def graph_blocking_io(fpath, domain):
    for x in merge_layers(trackgen(deserialize_generator(fpath))):
        yield x

def graph_cpu_bound(track, domain, cutdistance, maxdistance, cuttime, minscore=0.0000001):
    timesplit = partial(segment_tracks_timesplits, maxdelta=cuttime)
    distsplit = partial(segment_tracks_encode_greatcircledistance, cutdistance=cutdistance, maxdistance=maxdistance, cuttime=cuttime, minscore=minscore)
    geofenced = partial(fence_tracks,               domain=domain)
    #split_len = partial(max_tracklength,              max_track_length=10000)
    serialize = partial(serialize_network_edge,     domain=domain)
    print('processing mmsi', track['mmsi'], end='\r')
    #list(serialize(geofenced(split_len(distsplit(timesplit([track]))))))
    list(serialize(geofenced(distsplit(timesplit([track])))))
    return


def graph(fpath, domain, parallel=0, cutdistance=5000, maxdistance=200000, cuttime=timedelta(hours=24), minscore=0.0000001):
    ''' perform geofencing on vessel trajectories, then concatenate aggregated 
        transit statistics between nodes (zones) to create network edges from 
        vessel trajectories

        this function will call geofence() for each trajectory in parallel, 
        outputting serialized results to the tmp_dir directory. after 
        deserialization, the temporary files are removed, and output will be 
        written to 'output.csv' inside the data_dir directory

        args:
            tracks: dictionary generator 
                see track_gen.py for examples
            domain: ais.gis.Domain() class object
                collection of zones defined as polygons, these will
                be used as nodes in the network graph
            parallel: integer
                number of processes to compute geofencing in parallel.
                if set to 0 or False, no parallelization will be used
                
        returns: None
    '''
    if not parallel: 
        for track in graph_blocking_io(fpath, domain):
            graph_cpu_bound(track, domain=domain, cutdistance=cutdistance, maxdistance=maxdistance, cuttime=cuttime, minscore=minscore)
        print()

    else:
        with Pool(processes=parallel) as p:
            fcn = partial(graph_cpu_bound, domain=domain, cutdistance=cutdistance, maxdistance=maxdistance, cuttime=cuttime, minscore=minscore)
            p.imap_unordered(fcn, (tr for tr in graph_blocking_io(fpath, domain=domain)), chunksize=1)
            p.close()
            p.join()
        print()
