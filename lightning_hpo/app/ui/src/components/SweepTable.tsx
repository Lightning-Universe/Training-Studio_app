import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { Box, Button, IconButton, Link, Stack, Table } from 'lightning-ui/src/design-system/components';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { AppClient, SweepConfig, TensorboardConfig, TrialConfig } from '../generated';
import TableContainer from './TableContainer';

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

function trialToRows(trials: Record<string, TrialConfig>) {
  return Object.entries(trials).map(entry => [
    entry[0],
    <Status status={entry[1].status ? statusToEnum[entry[1].status] : StatusEnum.NOT_STARTED} />,
    String(entry[1].best_model_score),
    ...Object.entries(entry[1].params.params).map(value => String(value[1])),
    entry[1].exception,
  ]);
}

function generateTrialHeader(trialHeader: string[], params) {
  const paramsHeader = Object.entries(params).map(entry => entry[0]);
  return trialHeader.concat(paramsHeader).concat(['Exception']);
}

function createLoggerUrl(url?: string) {
  const cell = url ? (
    <Link href={url} target="_blank">
      Click Me !
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
    status: StatusEnum.RUNNING.toLowerCase(),
    desired_state: StatusEnum.RUNNING.toLowerCase(),
    url: undefined,
  });
}

function createLoggerControl(tensorboardConfig?: TensorboardConfig) {
  const status = tensorboardConfig?.status ? statusToEnum[tensorboardConfig.status] : StatusEnum.NOT_STARTED;
  if (status == StatusEnum.RUNNING) {
    return <Button onClick={_ => stopTensorboard(tensorboardConfig)} text="Stop" />;
  } else if (status == StatusEnum.STOPPED) {
    return <Button onClick={_ => runTensorboard(tensorboardConfig)} text="Run" />;
  } else {
    return <Status status={status} />;
  }
}

export function Sweeps(props: { sweeps: SweepConfig[]; tensorboards: TensorboardConfig[] }) {
  const sweepHeader = [
    'Name',
    'Status',
    'Number of trials',
    'Number of trials done',
    'Framework',
    'Cloud Compute',
    'Direction',
    'Logger URL',
    'Logger Control',
    'More',
  ];

  const baseTrialHeader = ['Name', 'Status', 'Best Model Score'];
  const tensorboardIdsToStatuses = Object.fromEntries(
    props.tensorboards.map(e => {
      return [e.sweep_id, e];
    }),
  );

  /* TODO: Merge the Specs */
  const rows = props.sweeps.map(sweep => {
    const tensorboardConfig =
      sweep.sweep_id in tensorboardIdsToStatuses ? tensorboardIdsToStatuses[sweep.sweep_id] : null;

    return [
      sweep.sweep_id,
      <Status status={sweep.status ? statusToEnum[sweep.status] : StatusEnum.NOT_STARTED} />,
      sweep.n_trials,
      sweep.trials_done,
      sweep.framework,
      sweep.cloud_compute,
      sweep.direction,
      createLoggerUrl(sweep.url),
      createLoggerControl(tensorboardConfig),
      <IconButton id={sweep.sweep_id + '-button'}>
        <MoreHorizIcon sx={{ fontSize: 16 }} />
      </IconButton>,
    ];
  });

  const rowDetails = props.sweeps.map(sweep => (
    <Stack>
      <TableContainer header={'Trials (' + sweep.trials[0].monitor + ')'}>
        <Table
          header={generateTrialHeader(baseTrialHeader, sweep.trials[0].params.params)}
          rows={trialToRows(sweep.trials)}
        />
      </TableContainer>
    </Stack>
  ));

  return (
    <TableContainer header="Sweeps">
      <Table header={sweepHeader} rows={rows} rowDetails={rowDetails} />
    </TableContainer>
  );
}
