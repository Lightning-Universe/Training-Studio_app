import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import { Box, Button, Link, Stack, Table, Typography } from 'lightning-ui/src/design-system/components';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { AppClient, ExperimentConfig, SweepConfig, TensorboardConfig } from '../generated';
import useClientDataState from '../hooks/useClientDataState';
import { getAppId } from '../utilities';
import BorderLinearProgress from './BorderLinearProgress';
import UserGuide, { UserGuideBody, UserGuideComment } from './UserGuide';

const appClient = new AppClient({
  BASE:
    window.location != window.parent.location
      ? document.referrer.replace(/\/$/, '').replace('/view/undefined', '')
      : document.location.href.replace(/\/$/, '').replace('/view/undefined', ''),
});

const statusToEnum = {
  not_started: StatusEnum.NOT_STARTED,
  pending: StatusEnum.PENDING,
  running: StatusEnum.RUNNING,
  pruned: StatusEnum.DELETED,
  succeeded: StatusEnum.SUCCEEDED,
  failed: StatusEnum.FAILED,
  stopped: StatusEnum.STOPPED,
} as { [k: string]: StatusEnum };

const ComputeToMachines = {
  'cpu': '1 CPU',
  'gpu': '1 T4',
  'gpu-fast': '1 V100',
  'gpu-fast-multi': '4 V100',
} as { [k: string]: string };

function createLoggerUrl(url?: string) {
  const cell = url ? (
    <Link href={url} target="_blank" underline="hover">
      <Stack direction="row" alignItems="center" spacing={0.5}>
        <OpenInNewIcon sx={{ fontSize: 20 }} />
        <Typography variant="subtitle2">Open</Typography>
      </Stack>
    </Link>
  ) : (
    <Box>{StatusEnum.NOT_STARTED}</Box>
  );

  return cell;
}

function stopTensorboard(tensorboardConfig?: TensorboardConfig) {
  appClient.appCommand.stopTensorboardCommandStopTensorboardPost({ sweep_id: tensorboardConfig.sweep_id });
}

function runTensorboard(tensorboardConfig?: TensorboardConfig) {
  appClient.appCommand.runTensorboardCommandRunTensorboardPost({
    id: tensorboardConfig.id,
    sweep_id: tensorboardConfig.sweep_id,
    shared_folder: tensorboardConfig.shared_folder,
    stage: StatusEnum.RUNNING.toLowerCase(),
    desired_stage: StatusEnum.RUNNING.toLowerCase(),
    url: undefined,
  });
}

function createLoggerControl(tensorboardConfig?: TensorboardConfig) {
  const status = tensorboardConfig?.stage ? statusToEnum[tensorboardConfig.stage] : StatusEnum.NOT_STARTED;
  if (status == StatusEnum.RUNNING) {
    return tensorboardConfig.url ? <Button onClick={_ => stopTensorboard(tensorboardConfig)} text="Stop" /> : null;
  } else if (status == StatusEnum.STOPPED) {
    return <Button onClick={_ => runTensorboard(tensorboardConfig)} text="Run" />;
  } else {
    return <Status status={status} />;
  }
}

function toCompute(sweep: SweepConfig) {
  if (sweep.num_nodes > 1) {
    return `${sweep.num_nodes} nodes x ${ComputeToMachines[sweep.cloud_compute]}`;
  } else {
    return `${ComputeToMachines[sweep.cloud_compute]}`;
  }
}

function toProgress(experiment: ExperimentConfig) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ width: '100%', mr: 1 }}>
        <BorderLinearProgress variant={experiment.progress == 0 ? null : 'determinate'} value={experiment.progress} />
      </Box>
      {experiment.progress ? (
        <Box sx={{ minWidth: 35 }}>
          <Typography variant="caption" display="block">{`${experiment.progress}%`}</Typography>
        </Box>
      ) : (
        <Box></Box>
      )}
    </Box>
  );
}

function startTime(experiment: ExperimentConfig) {
  return experiment.start_time ? String(experiment.start_time) : <Box></Box>;
}

export function Experiments() {
  const tensorboards = useClientDataState('tensorboards') as TensorboardConfig[];
  const sweeps = useClientDataState('sweeps') as SweepConfig[];

  const appId = getAppId();
  const enableClipBoard = appId == 'localhost' ? false : true;

  if (sweeps.length == 0) {
    return (
      <UserGuide title="Want to start a hyper-parameter sweep?" subtitle="Use the commands below in your terminal">
        <UserGuideComment>Connect to the app</UserGuideComment>
        <UserGuideBody enableClipBoard={enableClipBoard}>{`lightning connect ${appId} --yes`}</UserGuideBody>
        <UserGuideComment>Download example script</UserGuideComment>
        <UserGuideBody enableClipBoard={enableClipBoard}>
          {'wget https://raw.githubusercontent.com/Lightning-AI/lightning-hpo/master/examples/scripts/train.py'}
        </UserGuideBody>
        <UserGuideComment>Run a sweep</UserGuideComment>
        <UserGuideBody enableClipBoard={enableClipBoard}>
          lightning run sweep train.py --model.lr "[0.001, 0.01, 0.1]" --data.batch "[32, 64]"
          --algorithm="grid_search"
        </UserGuideBody>
      </UserGuide>
    );
  }

  const experimentHeader = [
    'Progress',
    'Name',
    'Best Score',
    'Compute',
    'Trainable Parameters',
    'Logger URL',
    'Start Time',
  ];

  const tensorboardIdsToStatuses = Object.fromEntries(
    tensorboards.map(e => {
      return [e.sweep_id, e];
    }),
  );

  var rows = sweeps.map(sweep => {
    const tensorboardConfig =
      sweep.sweep_id in tensorboardIdsToStatuses ? tensorboardIdsToStatuses[sweep.sweep_id] : null;

    return Object.entries(sweep.experiments).map(entry => [
      toProgress(entry[1]),
      entry[1].name,
      String(entry[1].best_model_score),
      toCompute(sweep),
      String(entry[1].total_parameters),
      createLoggerUrl(tensorboardConfig ? tensorboardConfig.url : sweep.logger_url),
      startTime(entry[1]),
    ]);
  });

  let flatArray = [].concat.apply([], rows);

  return <Table header={experimentHeader} rows={flatArray} />;
}
