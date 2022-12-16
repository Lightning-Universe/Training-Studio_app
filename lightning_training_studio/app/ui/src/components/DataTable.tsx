import { DataConfig } from 'generated';
import useClientDataState from 'hooks/useClientDataState';
import useShowHelpPageState, { HelpPageState } from 'hooks/useShowHelpPageState';
import { Table } from 'lightning-ui/src/design-system/components';
import { getAppId } from 'utilities';
import UserGuide, { UserGuideBody, UserGuideComment } from './UserGuide';

const DataTable = () => {
  const { showHelpPage, setShowHelpPage } = useShowHelpPageState();
  const data = useClientDataState('data') as DataConfig[];

  const appId = getAppId();

  if (data.length == 0) {
    setShowHelpPage(HelpPageState.forced);
  } else if (showHelpPage == HelpPageState.forced) {
    setShowHelpPage(HelpPageState.notShown);
  }

  if (showHelpPage == HelpPageState.forced || showHelpPage == HelpPageState.shown) {
    return (
      <UserGuide
        title="Use your own S3 datasets in your Sweeps & Experiments."
        subtitle="Use the commands below in your local terminal on your own computer.">
        <UserGuideComment>Connect to the app</UserGuideComment>
        <UserGuideBody>{`lightning connect ${appId}`}</UserGuideBody>
        <UserGuideComment>Add a dataset by providing its name and s3 source location</UserGuideComment>
        <UserGuideBody>
          {'lightning add dataset --name mnist --source s3://lightning-example-public/MNIST/'}
        </UserGuideBody>
        <UserGuideComment>
          Run an experiment using the newly added <b>mnist</b> dataset. The data are visible under{' '}
          <b>/content/data/MNIST/</b>
        </UserGuideComment>
        <UserGuideBody>{'lightning run experiment train.py --dataset mnist:/content/data/MNIST/'}</UserGuideBody>
      </UserGuide>
    );
  }

  const header = ['Name', 'Source', 'Default Mount Path'];

  const rows = data.map(data => {
    return [data.name, data.source, data.mount_path];
  });

  return <Table header={header} rows={rows} />;
};

export default DataTable;
