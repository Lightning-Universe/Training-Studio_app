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

const clientDataContext = React.createContext<{ [k: string]: any[] }>({});

export const ClientDataProvider = (props: { endpoint: keyof typeof clientEndpoints; children: React.ReactNode }) => {
  const [state, dispatch] = React.useReducer((state: { [k: string]: any[] }, newValue: { [k: string]: any[] }) => {
    return { ...newValue, ...state };
  }, {});

  useEffect(() => {
    clientEndpoints[props.endpoint](appClient).then(data => dispatch(Object.fromEntries([[props.endpoint, data]])));

    const interval = setInterval(() => {
      clientEndpoints[props.endpoint](appClient).then(data => dispatch(Object.fromEntries([[props.endpoint, data]])));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <clientDataContext.Provider value={state}>{props.children}</clientDataContext.Provider>;
};

const useClientDataState = (endpoint: keyof typeof clientEndpoints) => {
  const clientData = React.useContext(clientDataContext);

  return clientData[endpoint] || [];
};

export default useClientDataState;
