import React from 'react';

export enum HelpPageState {
  forced = 'forced',
  shown = 'shown',
  notShown = 'not shown',
}

const defaultShowHelpPage = HelpPageState.notShown;
const showHelpPageContext = React.createContext(defaultShowHelpPage);
const dispatchContext = React.createContext((newValue: HelpPageState): void => {});

// @ts-ignore
export const ShowHelpPageProvider = ({ children }) => {
  const [state, dispatch] = React.useReducer(
    (state: HelpPageState, newValue: HelpPageState) => newValue,
    defaultShowHelpPage,
  );
  return (
    <showHelpPageContext.Provider value={state}>
      <dispatchContext.Provider value={dispatch as (newValue: HelpPageState) => void}>
        {children}
      </dispatchContext.Provider>
    </showHelpPageContext.Provider>
  );
};

const useShowHelpPageState = () => {
  const showHelpPage = React.useContext(showHelpPageContext);
  const setShowHelpPage = React.useContext(dispatchContext);

  return {
    showHelpPage,
    setShowHelpPage,
  };
};

export default useShowHelpPageState;
