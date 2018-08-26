import React from 'react';
import {Query, Subscription} from 'react-apollo';
import gql from 'graphql-tag';


const QUERY = gql`
    query getHello ($name: String) {
        hello(name: $name)
    }
`;

const SUBS = gql`
    subscription countSeconds {
        countSeconds(upTo: 10)
    }
`;


export default function GqlQueryDemo() {
    return <div>
        <h2>Query demo</h2>
        <div>
            <Query query={QUERY} variables={{name: 'World'}}>
                {({data: {hello}}) => {
                     return hello || 'Loading...';
                }}
            </Query>
        </div>

        <h2>Subscription demo</h2>
        <div>
            <Subscription subscription={SUBS}>
                {({data}) => {
                     console.log('SUBSCRIPTION', data);
                     if (!data) {
                         return '---';
                     }
                     const {countSeconds} = data;
                     return `Seconds: ${countSeconds}`;
                }}

            </Subscription>
        </div>
    </div>;
}
