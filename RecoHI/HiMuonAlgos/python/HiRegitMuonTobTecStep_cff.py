import FWCore.ParameterSet.Config as cms

# pp iterative tracking modified for hiOffline reco (the vertex is the one reconstructed in HI)
################################### 6th step: very large impact parameter trackng using TOB+TEC ring 5 seeding --pair

from RecoHI.HiTracking.HITrackingRegionProducer_cfi import *
HiTrackingRegionFactoryFromSTAMuonsBlock.MuonTrackingRegionBuilder.vertexCollection = cms.InputTag("hiSelectedVertex")
HiTrackingRegionFactoryFromSTAMuonsBlock.MuonSrc= cms.InputTag("standAloneMuons","UpdatedAtVtx")

HiTrackingRegionFactoryFromSTAMuonsBlock.MuonTrackingRegionBuilder.UseVertex      = True

HiTrackingRegionFactoryFromSTAMuonsBlock.MuonTrackingRegionBuilder.UseFixedRegion = True
HiTrackingRegionFactoryFromSTAMuonsBlock.MuonTrackingRegionBuilder.Phi_fixed      = 0.3
HiTrackingRegionFactoryFromSTAMuonsBlock.MuonTrackingRegionBuilder.Eta_fixed      = 0.2

###################################
from  RecoTracker.IterativeTracking.TobTecStep_cff import *

# remove previously used clusters
hiRegitMuTobTecStepClusters = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepClusters.clone(
    oldClusterRemovalInfo = cms.InputTag("hiRegitMuPixelLessStepClusters"),
    trajectories     = cms.InputTag("hiRegitMuPixelLessStepTracks"),
    overrideTrkQuals = cms.InputTag('hiRegitMuPixelLessStepSelector','hiRegitMuPixelLessStep')
)

# SEEDING LAYERS
hiRegitMuTobTecStepSeedLayers =  RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepSeedLayers.clone(
    ComponentName    = cms.string('hiRegitMuTobTecStepSeedLayers'),
     )
hiRegitMuTobTecStepSeedLayers.TOB.skipClusters = cms.InputTag('hiRegitMuTobTecStepClusters')
hiRegitMuTobTecStepSeedLayers.TEC.skipClusters = cms.InputTag('hiRegitMuTobTecStepClusters')


# seeding
hiRegitMuTobTecStepSeeds     = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepSeeds.clone()
hiRegitMuTobTecStepSeeds.RegionFactoryPSet                                           = HiTrackingRegionFactoryFromSTAMuonsBlock.clone()
hiRegitMuTobTecStepSeeds.ClusterCheckPSet.doClusterCheck                             = False # do not check for max number of clusters pixel or strips
hiRegitMuTobTecStepSeeds.RegionFactoryPSet.MuonTrackingRegionBuilder.EscapePt        = 1.0
hiRegitMuTobTecStepSeeds.RegionFactoryPSet.MuonTrackingRegionBuilder.DeltaR          = 2.0 # default = 0.2
hiRegitMuTobTecStepSeeds.RegionFactoryPSet.MuonTrackingRegionBuilder.DeltaZ_Region   = 2.0 # this give you the length 
hiRegitMuTobTecStepSeeds.RegionFactoryPSet.MuonTrackingRegionBuilder.Rescale_Dz      = 20. # max(DeltaZ_Region,Rescale_Dz*vtx->zError())
hiRegitMuTobTecStepSeeds.OrderedHitsFactoryPSet.SeedingLayers                        = 'hiRegitMuTobTecStepSeedLayers'

# building: feed the new-named seeds
hiRegitMuTobTecStepInOutTrajectoryFilter = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepInOutTrajectoryFilter.clone(
    ComponentName        = 'hiRegitMuTobTecStepInOutTrajectoryFilter'
    )
hiRegitMuTobTecStepInOutTrajectoryFilter.filterPset.minPt         = 0.9 # after each new hit, apply pT cut for traj w/ at least minHitsMinPt = cms.int32(3),



hiRegitMuTobTecStepTrajectoryFilter = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepTrajectoryFilter.clone(
    ComponentName        = 'hiRegitMuTobTecStepTrajectoryFilter',
    )
hiRegitMuTobTecStepTrajectoryFilter.filterPset.minPt              = 0.9 # after each new hit, apply pT cut for traj w/ at least minHitsMinPt = cms.int32(3),


hiRegitMuTobTecStepTrajectoryBuilder = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepTrajectoryBuilder.clone(
    ComponentName             = 'hiRegitMuTobTecStepTrajectoryBuilder',
    trajectoryFilterName      = 'hiRegitMuTobTecStepTrajectoryFilter',
    inOutTrajectoryFilterName = 'hiRegitMuTobTecStepInOutTrajectoryFilter',
    clustersToSkip            = cms.InputTag('hiRegitMuTobTecStepClusters'),
)

hiRegitMuTobTecStepTrackCandidates        =  RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepTrackCandidates.clone(
    src               = cms.InputTag('hiRegitMuTobTecStepSeeds'),
    TrajectoryBuilder = 'hiRegitMuTobTecStepTrajectoryBuilder',
    maxNSeeds         = cms.uint32(1000000)
    )

# fitting: feed new-names
hiRegitMuTobTecStepTracks                 = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepTracks.clone(
    src                 = 'hiRegitMuTobTecStepTrackCandidates'
)

import RecoHI.HiTracking.hiMultiTrackSelector_cfi
hiRegitMuTobTecStepSelector               = RecoTracker.IterativeTracking.TobTecStep_cff.tobTecStepSelector.clone( 
    src                 ='hiRegitMuTobTecStepTracks',
    vertices            = cms.InputTag("hiSelectedVertex"),
    trackSelectors= cms.VPSet(
        RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiLooseMTS.clone(
            name = 'hiRegitMuTobTecStepLoose',
            ),
        RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiTightMTS.clone(
            name = 'hiRegitMuTobTecStepTight',
            preFilterName = 'hiRegitMuTobTecStepLoose',
            ),
        RecoHI.HiTracking.hiMultiTrackSelector_cfi.hiHighpurityMTS.clone(
            name = 'hiRegitMuTobTecStep',
            preFilterName = 'hiRegitMuTobTecStepTight',
            ),
        ) #end of vpset
  
)

hiRegitMuonTobTecStep = cms.Sequence(hiRegitMuTobTecStepClusters*
                                     hiRegitMuTobTecStepSeeds*
                                     hiRegitMuTobTecStepTrackCandidates*
                                     hiRegitMuTobTecStepTracks*
                                     hiRegitMuTobTecStepSelector)


