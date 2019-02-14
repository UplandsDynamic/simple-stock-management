import {configure} from "enzyme/build";
import Adapter from "enzyme-adapter-react-16";
import 'jest-enzyme';

const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};

const sessionStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
};

global.localStorage = localStorageMock;
global.sessionStorage = sessionStorageMock;

// set enzyme adapter
configure({adapter: new Adapter()});