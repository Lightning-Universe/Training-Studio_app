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

function trialToRows(trials: Record<string, ExperimentConfig>) {
  return Object.entries(trials).map(entry => [
    <Status status={entry[1].stage ? statusToEnum[entry[1].stage] : StatusEnum.NOT_STARTED} />,
    entry[0],
    String(entry[1].best_model_score),
    <Box sx={{ minWidth: 35 }}>
      <Typography variant="caption" display="block">{`${
        entry[1].progress == null ? '0' : entry[1].progress
      }%`}</Typography>
    </Box>,
    ...Object.entries(entry[1].params).map(value => String(value[1])),
    entry[1].exception,
  ]);
}

function generateTrialHeader(trialHeader: string[], params) {
  const paramsHeader = Object.entries(params).map(entry => entry[0]);
  return trialHeader.concat(paramsHeader).concat(['Exception']);
}

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

export function Sweeps() {
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
          lightning run sweep train.py --n_trials=3 --simultaneous_trials=1 --logger="tensorboard" --direction=maximize
          --cloud_compute=cpu-medium --model.lr="log_uniform(0.001, 0.01)" --model.gamma="uniform(0.5, 0.8)"
          --data.batch_size="categorical([32, 64])" --framework="pytorch_lightning" --requirements="torchvision, wandb,
          'jsonargparse[signatures]'"
        </UserGuideBody>
      </UserGuide>
    );
  }

  const sweepHeader = [
    'Status',
    'Name',
    'Monitor',
    'Progress',
    'Framework',
    'Cloud Compute',
    'Direction',
    'Logger URL',
    'Logger Control',
  ];

  const baseTrialHeader = ['Status', 'Name', 'Best Score', 'Progress'];
  const tensorboardIdsToStatuses = Object.fromEntries(
    tensorboards.map(e => {
      return [e.sweep_id, e];
    }),
  );

  /* TODO: Merge the Specs */
  const rows = sweeps.map(sweep => {
    const tensorboardConfig =
      sweep.sweep_id in tensorboardIdsToStatuses ? tensorboardIdsToStatuses[sweep.sweep_id] : null;

    const progress = sweep.trials_done ? Math.round(100 * (sweep.trials_done / sweep.n_trials)) : 0;

    const progressBar =
      progress == 100 ? (
        <Box sx={{ minWidth: 35 }}>
          <Typography variant="subtitle2">{`${progress}%`}</Typography>
        </Box>
      ) : (
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ width: '100%', mr: 1 }}>
            <BorderLinearProgress variant={progress == 0 ? null : 'determinate'} value={progress} />
          </Box>
          <Box sx={{ minWidth: 35 }}>
            <Typography variant="caption" display="block">{`${progress}%`}</Typography>
          </Box>
        </Box>
      );

    const monitor = sweep.trials[0]?.monitor || null;

    return [
      <Status status={sweep.stage ? statusToEnum[sweep.stage] : StatusEnum.NOT_STARTED} />,
      sweep.sweep_id,
      monitor,
      progressBar,
      sweep.framework,
      sweep.cloud_compute,
      sweep.direction,
      createLoggerUrl(tensorboardConfig ? tensorboardConfig.url : sweep.logger_url),
      tensorboardConfig ? createLoggerControl(tensorboardConfig) : null,
    ];
  });

  const rowDetails = sweeps.map(sweep => (
    <Stack>
      <Table header={generateTrialHeader(baseTrialHeader, sweep.trials[0].params)} rows={trialToRows(sweep.trials)} />
    </Stack>
  ));

  return <Table header={sweepHeader} rows={rows} rowDetails={rowDetails} />;
}
