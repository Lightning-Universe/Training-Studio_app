import MoreHorizIcon from '@mui/icons-material/MoreHoriz';
import { IconButton, Link, Stack, Table } from 'lightning-ui/src/design-system/components';
import Status, { StatusEnum } from 'lightning-ui/src/shared/components/Status';
import { SweepConfig, TensorboardConfig, TrialConfig } from '../generated';
import TableContainer from './TableContainer';

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
  ]);
}

function generateTrialHeader(trialHeader: string[], params) {
  const paramsHeader = Object.entries(params).map(entry => entry[0]);
  return trialHeader.concat(paramsHeader);
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
    'URL',
    'More',
  ];
  const baseTrialHeader = ['Name', 'Status', 'Best Model Score'];

  const rows = props.sweeps.map(sweep => [
    sweep.sweep_id,
    <Status status={sweep.status ? statusToEnum[sweep.status] : StatusEnum.NOT_STARTED} />,
    sweep.n_trials,
    sweep.trials_done,
    sweep.framework,
    sweep.cloud_compute,
    sweep.direction,
    <Link href={sweep.url} target="_blank">
      Click Me
    </Link>,
    <IconButton id={sweep.sweep_id + '-button'}>
      <MoreHorizIcon sx={{ fontSize: 16 }} />
    </IconButton>,
  ]);

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
