import React, { useEffect } from 'react';
import { AppClient } from '../generated';

const appClient = new AppClient({
  BASE:
    window.location != window.parent.location
      ? document.referrer.replace(/\/$/, '')
      : document.location.href.replace(/\/$/, ''),
});

const clientEndpoints = {
  sweeps: (appClient: AppClient) => appClient.appClientCommand.showSweepsCommandShowSweepsPost(),
  notebooks: (appClient: AppClient) => appClient.appClientCommand.showNotebooksCommandShowNotebooksPost(),
  tensorboards: (appClient: AppClient) => appClient.appCommand.showTensorboardsCommandShowTensorboardsPost(),
};

const clientDataContexts = {
  sweeps: React.createContext<any[]>([]),
  notebooks: React.createContext<any[]>([]),
  tensorboards: React.createContext<any[]>([]),
};

export const ClientDataProvider = (props: { endpoint: keyof typeof clientEndpoints; children: React.ReactNode }) => {
  const [state, dispatch] = React.useReducer((state: any[], newValue: any[]) => newValue, []);

  useEffect(() => {
    clientEndpoints[props.endpoint](appClient).then(data => dispatch(data));

    const interval = setInterval(() => {
      clientEndpoints[props.endpoint](appClient).then(data => dispatch(data));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const context = clientDataContexts[props.endpoint];
  return <context.Provider value={state}>{props.children}</context.Provider>;
};

const useClientDataState = (endpoint: keyof typeof clientEndpoints) => {
  const clientData = React.useContext(clientDataContexts[endpoint]);

  return clientData;
};

export default useClientDataState;
