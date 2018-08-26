import React from 'react';
import {Component} from 'react';

import GqlQueryDemo from 'ui/gql-query-demo';
import ApolloProvider from 'lib/apollo-provider';

import './App.css';


export default class App extends Component {
    state = {
        name: 'web-client'
    };

    render() {
        return (
            <ApolloProvider>
                <div className="App">
                    <h1>Welcome to {this.state.name}</h1>

                    <GqlQueryDemo />
                </div>
            </ApolloProvider>
        );
    }
}
