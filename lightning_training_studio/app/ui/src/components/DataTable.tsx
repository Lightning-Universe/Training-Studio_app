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
      <UserGuide title="Want to add data?" subtitle="Use the commands below in your terminal">
        <UserGuideComment>Connect to the app</UserGuideComment>
        <UserGuideBody>{`lightning connect ${appId} --yes`}</UserGuideBody>
        <UserGuideComment>Add data from an S3 bucket</UserGuideComment>
        <UserGuideBody>{'lightning create data --name example --source s3://pl-flash-data/wiki-test/'}</UserGuideBody>
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
