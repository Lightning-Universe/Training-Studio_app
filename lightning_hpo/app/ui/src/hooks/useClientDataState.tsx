import { useSnackbar } from 'lightning-ui/src/design-system/components';
import React, { useEffect } from 'react';
import { AppClient } from '../generated';
import { getUrl } from '../utilities';

export const appClient = new AppClient({
  BASE: getUrl(),
});

const clientEndpoints = {
  sweeps: (appClient: AppClient) => appClient.appClientCommand.showSweepsCommandShowSweepsPost(),
  tensorboards: (appClient: AppClient) => appClient.appApi.showTensorboardsApiShowTensorboardsPost(),
  data: (appClient: AppClient) => appClient.appClientCommand.showDataCommandShowDataPost(),
};

const clientDataContexts = {
  sweeps: React.createContext<any[]>([]),
  tensorboards: React.createContext<any[]>([]),
  data: React.createContext<any[]>([]),
};

export const ClientDataProvider = (props: { endpoint: keyof typeof clientEndpoints; children: React.ReactNode }) => {
  const [isErrorState, setIsErrorState] = React.useState(false);
  const [state, dispatch] = React.useReducer((state: any[], newValue: any[]) => newValue, []);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    const post = () => {
      clientEndpoints[props.endpoint](appClient)
        .then(data => {
          if (isErrorState) {
            setIsErrorState(false);
          }
          dispatch(data);
        })
        .catch(error => {
          if (!isErrorState) {
            setIsErrorState(true);
            enqueueSnackbar({
              title: 'Error Fetching Data',
              children: 'Try reloading the page',
              severity: 'error',
            });
          }
        });
    };

    post();

    const interval = setInterval(() => {
      post();
    }, 1000);

    return () => clearInterval(interval);
  }, [isErrorState]);

  const context = clientDataContexts[props.endpoint];
  return <context.Provider value={state}>{props.children}</context.Provider>;
};

const useClientDataState = (endpoint: keyof typeof clientEndpoints) => {
  const clientData = React.useContext(clientDataContexts[endpoint]);

  return clientData;
};

export default useClientDataState;
