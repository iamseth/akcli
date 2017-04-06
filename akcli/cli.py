import os
import sys
import pprint
import logging
import ConfigParser
import json as _json

import click

import akcli

SUPPORTED_RECORD_TYPES = ['A', 'CNAME', 'NS']


class Context(object):
    pass


@click.group()
@click.option('--debug', is_flag=True, help='Enables debug mode.')
@click.option('--json', is_flag=True, help='Output as JSON.')
@click.option('--config', type=click.File(), default='{}/.akamai.cfg'.format(os.path.expanduser("~")))
@click.version_option(akcli.__version__)
@click.pass_context
def cli(ctx, debug, json, config):
    ctx.obj = Context()
    lvl = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=lvl, format='%(asctime)s %(levelname)s %(message)s')
    ctx.obj.json = json
    ctx.obj.config = ConfigParser.ConfigParser()
    ctx.obj.config.readfp(config)


@cli.group()
@click.pass_context
def dns(ctx):
    baseurl = ctx.obj.config.get('auth', 'baseurl')
    client_token = ctx.obj.config.get('auth', 'client_token')
    client_secret = ctx.obj.config.get('auth', 'client_secret')
    access_token = ctx.obj.config.get('auth', 'access_token')
    ctx.obj.akamai_dns = akcli.dns.AkamaiDNS(baseurl, client_token, client_secret, access_token)


@dns.command()
@click.argument('zone')
@click.argument('name')
@click.argument('type', type=click.Choice(SUPPORTED_RECORD_TYPES))
@click.argument('target')
@click.option('--ttl', type=click.INT, default=600, help='TTL value in seconds, such as 86400')
@click.pass_context
def add_record(ctx, zone, name, type, target, ttl):
    successful = ctx.obj.akamai_dns.add_record(zone_name=zone, record_type=type, name=name, target=target, ttl=ttl)
    if successful:
        click.echo(_json.dumps("Record added successfully."))
    else:
        click.echo(_json.dumps("Failed to add record."))
        sys.exit(1)


@dns.command()
@click.argument('zone')
@click.argument('name')
@click.argument('type', type=click.Choice(SUPPORTED_RECORD_TYPES))
@click.pass_context
def fetch_records(ctx, zone, name, type):
    records = ctx.obj.akamai_dns.fetch_records(zone_name=zone, record_type=type, name=name)
    if ctx.obj.json:
        click.echo(_json.dumps(records))
    else:
        for record in records:
            click.echo('{name:30}{type:20}{target:20}{ttl:10}'.format(**record))


@dns.command()
@click.argument('zone')
@click.argument('name')
@click.argument('type', type=click.Choice(SUPPORTED_RECORD_TYPES))
@click.argument('target')
@click.pass_context
def remove_record(ctx, zone, name, type, target):
    successful = ctx.obj.akamai_dns.remove_record(zone_name=zone, record_type=type, name=name, target=target)
    if successful:
        click.echo('Record has been removed.')
    else:
        click.echo('Unable to remove record.')
        sys.exit(1)

@dns.command()
@click.argument('zone')
@click.pass_context
def fetch_zone(ctx, zone):
    zone = ctx.obj.akamai_dns.fetch_zone(zone_name=zone)
    if ctx.obj.json:
        click.echo(_json.dumps(zone))
    else:
        printer = pprint.PrettyPrinter(indent=4)
        printer.pprint(zone)


@dns.command()
@click.argument('zone')
@click.argument('type', required=False, type=click.Choice(SUPPORTED_RECORD_TYPES))
@click.pass_context
def list_records(ctx, zone, type):
    records = ctx.obj.akamai_dns.list_records(zone_name=zone, record_type=type)
    if ctx.obj.json:
        click.echo(_json.dumps(records))
    else:
        for record in records:
            click.echo('{name:30}{type:20}{target:20}{ttl:10}'.format(**record))
