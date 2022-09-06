import React from 'react';

const defaultSelectedTab = 0;
const selectedTabContext = React.createContext(defaultSelectedTab);
const dispatchContext = React.createContext((newValue: number): void => {});

// @ts-ignore
export const SelectedTabProvider = ({ children }) => {
  const [state, dispatch] = React.useReducer((state: number, newValue: number) => newValue, defaultSelectedTab);
  return (
    <selectedTabContext.Provider value={state}>
      <dispatchContext.Provider value={dispatch as (newValue: number) => void}>{children}</dispatchContext.Provider>
    </selectedTabContext.Provider>
  );
};

const useSelectedTabState = () => {
  const selectedTab = React.useContext(selectedTabContext);
  const setSelectedTab = React.useContext(dispatchContext);

  return {
    selectedTab,
    setSelectedTab,
  };
};

export default useSelectedTabState;
